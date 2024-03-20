from pyrogram import Client, filters
from mfinder.db.settings_sql import (
    get_admin_settings,
    set_repair_mode,
    set_auto_delete,
    set_custom_caption,
    set_force_sub,
    set_channel_link,
    get_link,
    set_username,
)
from mfinder.db.ban_sql import is_banned, ban_user, unban_user
from mfinder.db.filters_sql import add_filter, rem_filter, list_filters
from mfinder.db.files_sql import count_files
from mfinder import ADMINS, DB_CHANNELS


@Client.on_message(filters.command(["autodelete"]) & filters.user(ADMINS))
async def auto_delete_(bot, update):
    data = update.text.split()
    if len(data) == 2:
        dur = data[-1]
        if dur.lower() == "off":
            dur = 0

        await set_auto_delete(int(dur))

        if dur:
            await update.reply_text(f"File auto delete set to `{dur}` seconds")
        else:
            await update.reply_text("File auto delete disabled")

    else:
        await update.reply_text("Please send in proper format `/autodelete seconds`")


@Client.on_message(filters.command(["repairmode"]) & filters.user(ADMINS))
async def repair_mode_(bot, update):
    data = update.text.split()
    if len(data) == 2:
        toggle = data[-1]
        if toggle.lower() == "off":
            mode = False
        elif toggle.lower() == "on":
            mode = True
        else:
            await update.reply_text(
                "Please send in proper format `/repairmode <on/off>`"
            )
            return

        await set_repair_mode(mode)
        await update.reply_text(f"Repair mode set to `{toggle.upper()}`")

    else:
        await update.reply_text("Please send in proper format `/repairmode on/off`")
        return


@Client.on_message(filters.command(["customcaption"]) & filters.user(ADMINS))
async def custom_caption_(bot, update):
    data = update.text.split()
    caption = " ".join(data[1:])
    if len(data) >= 2:
        if caption.lower() == "off":
            caption = None

        await set_custom_caption(caption)

        if caption:
            await update.reply_text(f"Custom caption set to `{caption}`")
        else:
            await update.reply_text("Custom caption disabled")

    else:
        await update.reply_text(
            "Please send in proper format `/customcaption caption/off`"
        )
        return


@Client.on_message(filters.command(["adminsettings"]))
async def admin_settings_(bot, update):
    user_id = update.from_user.id
    admin_settings = await get_admin_settings()
    auto_delete = admin_settings.auto_delete
    custom_caption = admin_settings.custom_caption
    fsub_channel = admin_settings.fsub_channel
    caption_uname = admin_settings.caption_uname
    invite_link = admin_settings.channel_link
    repair_mode = admin_settings.repair_mode

    admins = ""
    dbchannel = ""
    for admin in ADMINS:
        admins += "\n" + "`" + str(admin) + "`"
    for channel in DB_CHANNELS:
        dbchannel += "\n" + "`" + str(channel) + "`"

    if auto_delete:
        auto_delete = f"{auto_delete} seconds"
    else:
        auto_delete = "Disabled"

    if not custom_caption:
        custom_caption = "Disabled"

    if not fsub_channel:
        fsub_channel = "Disabled"

    if not caption_uname:
        caption_uname = "Disabled"

    if not invite_link:
        invite_link = "Disabled"

    if repair_mode:
        repair_mode = "Enabled"
    else:
        repair_mode = "Disabled"

    await bot.send_message(
        chat_id=user_id,
        text=f"**Below are your current settings.**\n\n**Repair Mode:** `{repair_mode}`\n**Auto Delete:** `{auto_delete}`\n**Custom Caption:** `{custom_caption}`\n**Force Sub:** `{fsub_channel}`\n**Caption Username:** `{caption_uname}`\n**Channel Link:** `{invite_link}`\n**Admins:** {admins} \n**DB Channels:** {dbchannel}",
    )


@Client.on_message(filters.command(["ban"]) & filters.user(ADMINS))
async def banuser(bot, update):
    data = update.text.split()
    if len(data) == 2:
        user_id = data[-1]
        banned = await is_banned(int(user_id))
        if not banned:
            await ban_user(int(user_id))
            await update.reply_text(f"User {user_id} banned")
        else:
            await update.reply_text(f"User {user_id} is already banned")

    else:
        await update.reply_text("Please send in proper format `/ban user_id`")


@Client.on_message(filters.command(["unban"]) & filters.user(ADMINS))
async def unbanuser(bot, update):
    data = update.text.split()
    if len(data) == 2:
        user_id = data[-1]
        banned = await is_banned(int(user_id))
        if banned:
            await unban_user(int(user_id))
            await update.reply_text(f"User {user_id} unbanned")
        else:
            await update.reply_text(f"User {user_id} is not in ban list")
    else:
        await update.reply_text("Please send in proper format `/unban user_id`")


@Client.on_message(filters.command(["addfilter"]) & filters.user(ADMINS))
async def addfilter(bot, update):
    data = update.text.split()
    if len(data) >= 3:
        fltr = data[1].lower()
        message = " ".join(data[2:])
        add = await add_filter(fltr, message)
        if add:
            await update.reply_text(f"Filter `{fltr}` added")
        else:
            await update.reply_text(f"Filter `{fltr}` already exists")
    else:
        await update.reply_text(
            "Please send in proper format `/addfilter filter message`"
        )


@Client.on_message(filters.command(["delfilter"]) & filters.user(ADMINS))
async def delfilter(bot, update):
    data = update.text.split()
    if len(data) == 2:
        fltr = data[-1].lower()
        rem = await rem_filter(fltr)
        if rem:
            await update.reply_text(f"Filter `{fltr}` removed")
        else:
            await update.reply_text(f"Filter `{fltr}` not found")
    else:
        await update.reply_text("Please send in proper format `/delfilter filter`")


@Client.on_message(filters.command(["listfilters"]) & filters.user(ADMINS))
async def list_filter(bot, update):
    fltr = await list_filters()
    fltr_msg = ""
    if fltr:
        for fltrs in fltr:
            fltr_msg += "\n" + "`" + fltrs + "`"
        await update.reply_text(f"**Available Filters:** {fltr_msg}")
    else:
        await update.reply_text("No filters found")


@Client.on_message(filters.command(["forcesub"]) & filters.user(ADMINS))
async def force_sub(bot, update):
    data = update.text.split()
    if len(data) == 2:
        channel = data[-1]
        if channel.lower() == "off":
            channel = 0

        if channel:
            try:
                link = await bot.create_chat_invite_link(channel)
                await set_channel_link(link.invite_link)
            except Exception as e:
                await update.reply_text(
                    f" Error while creating channel invite link: {str(e)}"
                )
                return

            await set_force_sub(int(channel))
            await update.reply_text(f"Force Subscription channel set to `{channel}`")
        else:
            await set_channel_link(None)
            await update.reply_text("Force Subscription disabled")

    else:
        await update.reply_text(
            "Please send in proper format `/forcesub channel_id/off`"
        )


@Client.on_message(filters.command(["checklink"]) & filters.user(ADMINS))
async def testlink(bot, update):
    link = await get_link()
    if link:
        await update.reply_text(f"Invite link for force subscription channel: {link}")
    else:
        await update.reply_text(
            "Force Subscription is disabled, please enable it first"
        )


@Client.on_message(filters.command(["setusername"]) & filters.user(ADMINS))
async def caption_username(bot, update):
    data = update.text.split()
    if len(data) == 2:
        username = data[-1]
        if username.lower() == "off":
            username = 0
        elif username.startswith("@"):
            username = username
        else:
            await update.reply_text("This is not a username, please check.")
            return

        await set_username(username)

        if username:
            await update.reply_text(f"File caption username set to `{username}`")
        else:
            await update.reply_text("File caption username disabled")

    else:
        await update.reply_text(
            "Please send in proper format `/setusername username/off`"
        )


@Client.on_message(filters.command(["total"]) & filters.user(ADMINS))
async def count_f(bot, update):
    count = await count_files()
    await update.reply_text(f"**Total no. of files in DB:** `{count}`")
