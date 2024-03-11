from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from mfinder import LOGGER, ADMINS
from mfinder.db.settings_sql import get_search_settings, change_search_settings


@Client.on_message(filters.command(["settings"]))
async def user_settings(bot, update):
    user_id = update.from_user.id
    precise_mode, button_mode, link_mode, set_kb = await find_search_settings(user_id)
    await bot.send_message(
        chat_id=user_id,
        text=f"**Below are your current settings.**\n\n**Precise Search Mode:** `{precise_mode}`\n**Button Result Mode:** `{button_mode}`\n**Link Result Mode:** `{link_mode}`",
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

    precise_mode, button_mode, link_mode, set_kb = await find_search_settings(user_id)

    await query.message.edit(
        text=f"**Below are your current settings.**\n\n**Precise Search Mode:** `{precise_mode}`\n**Button Result Mode:** `{button_mode}`\n**Link Result Mode:** `{link_mode}`",
        reply_markup=set_kb,
    )


@Client.on_callback_query(filters.regex(r"^btnn (.+)$"))
async def set_button_mode(bot, query):
    user_id = query.from_user.id
    btn_mode = query.data.split()[1]
    if btn_mode == "on":
        await change_search_settings(user_id, button_mode=True, link_mode=False)
    if btn_mode == "off":
        await change_search_settings(user_id, button_mode=False)
    if btn_mode == "md":
        await query.answer(text="Toggle Button/List Mode", show_alert=False)
        return

    precise_mode, button_mode, link_mode, set_kb = await find_search_settings(user_id)

    await query.message.edit(
        text=f"**Below are your current settings.**\n\n**Precise Search Mode:** `{precise_mode}`\n**Button Result Mode:** `{button_mode}`\n**Link Result Mode:** `{link_mode}`",
        reply_markup=set_kb,
    )


@Client.on_callback_query(filters.regex(r"^link (.+)$"))
async def set_link_mode(bot, query):
    user_id = query.from_user.id
    link_mode = query.data.split()[1]
    if link_mode == "on":
        await change_search_settings(user_id, button_mode=False, link_mode=True)
    if link_mode == "off":
        await change_search_settings(user_id, link_mode=False)
    if link_mode == "md":
        await query.answer(text="Toggle Link/List Mode", show_alert=False)
        return

    precise_mode, button_mode, link_mode, set_kb = await find_search_settings(user_id)

    await query.message.edit(
        text=f"**Below are your current settings.**\n\n**Precise Search Mode:** `{precise_mode}`\n**Button Result Mode:** `{button_mode}`\n**Link Result Mode:** `{link_mode}`",
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
        InlineKeyboardButton("Button Mode:", callback_data="btnn md"),
    ]

    b_on_kb = InlineKeyboardButton("Turn ON", callback_data="btnn on")
    b_off_kb = InlineKeyboardButton("Turn OFF", callback_data="btnn off")

    if search_settings:
        button_mode = search_settings.button_mode
        if button_mode:
            button_mode = "ON"
            bkb.append(b_off_kb)
        else:
            button_mode = "OFF"
            bkb.append(b_on_kb)
    else:
        await change_search_settings(user_id)
        button_mode = "OFF"
        bkb.append(b_on_kb)

    lkb = [
        InlineKeyboardButton("Link Mode:", callback_data="link md"),
    ]

    l_on_kb = InlineKeyboardButton("Turn ON", callback_data="link on")
    l_off_kb = InlineKeyboardButton("Turn OFF", callback_data="link off")

    if search_settings:
        link_mode = search_settings.link_mode
        if link_mode:
            link_mode = "ON"
            lkb.append(l_off_kb)
        else:
            link_mode = "OFF"
            lkb.append(l_on_kb)
    else:
        await change_search_settings(user_id)
        link_mode = "OFF"
        lkb.append(l_on_kb)

    set_kb = InlineKeyboardMarkup([kb, bkb, lkb])

    return precise_mode, button_mode, link_mode, set_kb
