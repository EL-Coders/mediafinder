from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from mfinder import LOGGER, ADMINS
from mfinder.db.settings_sql import get_search_settings, change_search_settings


@Client.on_message(filters.command(["settings"]))
async def user_settings(bot, update):
    user_id = update.from_user.id
    precise_mode, res_mode, set_kb = await find_search_settings(user_id)
    await bot.send_message(
        chat_id=user_id,
        text=f"**Below are your current settings:**\n\n**Precise Search Mode:** `{precise_mode}`\n**Result Mode:** `{res_mode}`\n\n__You can toggle settings with right side buttons__",
        reply_markup=set_kb,
    )


@Client.on_callback_query(filters.regex(r"^prec (.+)$"))
async def set_precise_mode(bot, query):
    user_id = query.from_user.id
    prsc_mode = query.data.split()[1]
    if prsc_mode == "on":
        await change_search_settings(user_id, precise_mode=True)
    if prsc_mode == "off":
        await change_search_settings(user_id, precise_mode=False)
    if prsc_mode == "md":
        await query.answer(text="Toggle Precise Search ON/OFF", show_alert=False)
        return

    precise_mode, res_mode, set_kb = await find_search_settings(user_id)

    await query.message.edit(
        text=f"**Below are your current settings:**\n\n**Precise Search Mode:** `{precise_mode}`\n**Result Mode:** `{res_mode}`\n\n__You can toggle settings with right side buttons__",
        reply_markup=set_kb,
    )


@Client.on_callback_query(filters.regex(r"^res (.+)$"))
async def set_list_mode(bot, query):
    user_id = query.from_user.id
    result_mode = query.data.split()[1]
    if result_mode == "btnn":
        await change_search_settings(
            user_id, button_mode=True, link_mode=False, list_mode=False
        )
    if result_mode == "link":
        await change_search_settings(
            user_id, button_mode=False, link_mode=True, list_mode=False
        )
    if result_mode == "list":
        await change_search_settings(
            user_id, button_mode=False, link_mode=False, list_mode=True
        )
    if result_mode == "mode":
        await query.answer(text="Toggle Button/Link/List Mode", show_alert=False)
        return

    precise_mode, res_mode, set_kb = await find_search_settings(user_id)

    await query.message.edit(
        text=f"**Below are your current settings:**\n\n**Precise Search Mode:** `{precise_mode}`\n**Result Mode:** `{res_mode}`\n\n__You can toggle settings with right side buttons__",
        reply_markup=set_kb,
    )


async def find_search_settings(user_id):
    search_settings = await get_search_settings(user_id)

    kb = [
        InlineKeyboardButton("Precise Mode:", callback_data="prec md"),
    ]

    on_kb = InlineKeyboardButton("Turn ON", callback_data="prec on")
    off_kb = InlineKeyboardButton("Turn OFF", callback_data="prec off")

    if search_settings:
        precise_mode = search_settings.precise_mode
        if precise_mode:
            precise_mode = "ON"
            kb.append(off_kb)
        else:
            precise_mode = "OFF"
            kb.append(on_kb)
    else:
        await change_search_settings(user_id)
        precise_mode = "OFF"
        kb.append(on_kb)

    bkb = [
        InlineKeyboardButton("Result Mode:", callback_data="res mode"),
    ]

    btn_kb = InlineKeyboardButton("Switch to Button", callback_data="res btnn")
    link_kb = InlineKeyboardButton("Switch to Link", callback_data="res link")
    list_kb = InlineKeyboardButton("Switch to List", callback_data="res list")

    if search_settings:
        button_mode = search_settings.button_mode
        link_mode = search_settings.link_mode
        list_mode = search_settings.list_mode
        if button_mode:
            bkb.append(link_kb)
            res_mode = "Button"
        elif link_mode:
            bkb.append(list_kb)
            res_mode = "Link"
        elif list_mode:
            bkb.append(btn_kb)
            res_mode = "List"
    else:
        await change_search_settings(user_id)
        bkb.append(btn_kb)

    set_kb = InlineKeyboardMarkup([kb, bkb])

    return precise_mode, res_mode, set_kb
