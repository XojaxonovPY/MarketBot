import asyncio
import logging
import sys
import bcrypt
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, Update
from aiogram.utils.i18n import I18n, FSMI18nMiddleware
import uvicorn
from uvicorn import Config, Server

from bot.handlera.main_handler import CustomMiddleware
from bot.handlera import dp
from utils.env_data import BotConfig
from db.model import db

TOKEN = BotConfig.TOKEN


async def on_startup(bot: Bot):
    db.init()
    await db.create_all()

    commands = [
        BotCommand(command="/start", description="Botni ishga tushirish"),
        BotCommand(command="/channel", description="Kanal ID sini yuborish"),
    ]
    await bot.set_my_commands(commands)
    print(bcrypt.hashpw("3".encode(), salt=bcrypt.gensalt()))


async def webhook_handler(request: web.Request):
    if request.path == f"/webhook/{TOKEN}":
        data = await request.json()
        update = Update(**data)
        await dp.feed_webhook_update(bot, update)
        return web.Response()
    return web.Response(status=404)


async def create_app():
    """AIOHTTP ilovasini yaratish"""
    app = web.Application()
    app.router.add_post(f"/webhook/{TOKEN}", webhook_handler)

    # Health check uchun endpoint
    async def health_check(request):
        return web.Response(text="OK")

    app.router.add_get("/health", health_check)
    return app


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    global bot
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Til middleware
    i18n = I18n(path='locales', default_locale='uz', domain='messages')
    dp.update.outer_middleware(FSMI18nMiddleware(i18n))
    dp.message.outer_middleware(CustomMiddleware())

    # Ishga tushganda
    await on_startup(bot)

    # Webhook sozlamalari
    WEBHOOK_URL = f"{BotConfig.WEBHOOK_URL}/webhook/{TOKEN}"
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)

    # Uvicorn serverini ishga tushirish
    app = await create_app()
    config = Config(
        app=app,
        host="0.0.0.0",
        port=10000,
        log_level="info",
        lifespan="off"  # AIOHTTP lifespan ni o'zi boshqaradi
    )
    server = Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())