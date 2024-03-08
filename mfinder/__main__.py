import uvloop
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
from mfinder import APP_ID, API_HASH, BOT_TOKEN

uvloop.install()


async def main():
    plugins = dict(root="mfinder/plugins")
    app = Client(
        name="mfinder",
        api_id=APP_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=plugins,
    )
    async with app:
        me = await app.get_me()
        print(
            f"{me.first_name} - @{me.username} - Pyrogram v{__version__} (Layer {layer}) - Started..."
        )
        await idle()
        print(f"{me.first_name} - @{me.username} - Stopped !!!")

uvloop.run(main())
