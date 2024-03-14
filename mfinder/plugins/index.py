import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from mfinder import ADMINS, LOGGER
from mfinder.db.files_sql import save_file, delete_file
from mfinder.utils.helpers import edit_caption


lock = asyncio.Lock()
media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.private & filters.user(ADMINS) & media_filter)
async def index_files(bot, message):
    user_id = message.from_user.id
    if lock.locked():
        await message.reply("Wait until previous process complete.")
    else:

        try:
            last_msg_id = message.forward_from_message_id
            if message.forward_from_chat.username:
                chat_id = message.forward_from_chat.username
            else:
                chat_id = message.forward_from_chat.id
            await bot.get_messages(chat_id, last_msg_id)

            kb = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Proceed", callback_data=f"index {chat_id} {last_msg_id}"
                        )
                    ],
                    [InlineKeyboardButton("Cancel", callback_data="can-index")],
                ]
            )
            await bot.send_message(
                user_id,
                "Please confirm if you want to start indexing",
                reply_markup=kb,
            )
        except Exception as e:
            await message.reply_text(
                f"Unable to start indexing, either the channel is private and bot is not an admin in the forwarded chat, or you forwarded message as copy.\nError caused due to <code>{e}</code>"
            )


@Client.on_callback_query(filters.regex(r"^index -?\d+ \d+"))
async def index(bot, query):
    user_id = query.from_user.id
    chat_id, last_msg_id = map(int, query.data.split()[1:])

    await query.message.delete()
    msg = await bot.send_message(user_id, "Processing Index...⏳")
    total_files = 0
    async with lock:
        try:
            total = last_msg_id + 1
            current = 2
            counter = 0
            while True:
                try:
                    message = await bot.get_messages(
                        chat_id=chat_id, message_ids=current, replies=0
                    )
                except FloodWait as e:
                    LOGGER.warning("FloodWait while indexing, Error: %s", str(e))
                    await asyncio.sleep(e.value)
                except Exception as e:
                    LOGGER.warning("Error occurred while fetching message: %s", str(e))
                try:
                    for file_type in ("document", "video", "audio"):
                        media = getattr(message, file_type, None)
                        if not media:
                            break
                        file_name = media.file_name
                        file_name = edit_caption(file_name)
                        media.file_type = file_type
                        media.caption = file_name
                        await save_file(media)
                        total_files += 1
                except Exception as e:
                    LOGGER.warning("Error occurred while saving file: %s", str(e))

                current += 1
                counter += 1
                if counter == 20:
                    await msg.edit(
                        f"Total messages fetched: {current}\nTotal messages saved: {total_files}"
                    )
                    counter -= 20
                if current == total:
                    break

        except Exception as e:
            LOGGER.exception(e)
            await msg.edit(f"Error: {e}")
        else:
            await msg.edit(f"Total {total_files} Saved To DataBase!")


@Client.on_message(filters.command(["index"]) & filters.user(ADMINS))
async def index_comm(bot, update):
    await update.reply(
        "Now please forward the last message of the channel you want to index & follow the steps. Bot must be admin of the channel if the channel is private."
    )


@Client.on_message(filters.command(["delete"]) & filters.user(ADMINS))
async def delete_files(bot, message):
    if not message.reply_to_message:
        await message.reply("Please reply to a file to delete")
    org_msg = message.reply_to_message
    try:
        for file_type in ("document", "video", "audio"):
            media = getattr(org_msg, file_type, None)
            if not media:
                break
            del_file = await delete_file(media)
            if del_file == "Not Found":
                await message.reply(f"`{media.file_name}` not found in database")
            elif del_file == True:
                await message.reply(f"`{media.file_name}` deleted from database")
            else:
                await message.reply(
                    f"Error occurred while deleting `{media.file_name}`, please check logs for more info"
                )
    except Exception as e:
        LOGGER.warning("Error occurred while deleting file: %s", str(e))


@Client.on_callback_query(filters.regex(r"^can-index$"))
async def cancel_index(bot, query):
    await query.message.delete()
