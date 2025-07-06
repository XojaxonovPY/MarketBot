import asyncio
import logging

import uvicorn
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

TOKEN = "YOUR_BOT_TOKEN"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://marketbot-jqcl.onrender.com" + WEBHOOK_PATH


async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)


async def main():
    # Bot va dispatcher yaratish
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.startup.register(on_startup)

    # AIOHTTP ilova yaratish
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Health check endpoint
    async def health_check(request):
        return web.Response(text="OK")

    app.router.add_get("/health", health_check)

    # Uvicorn serverini ishga tushirish
    config = uvicorn.Config(
        app,  # Bu yerda ASGI ilova kerak emas
        host="0.0.0.0",
        port=10000,
        log_level=logging.INFO,
        interface="asgi3",  # ASGI interfeysini aniq belgilash
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())