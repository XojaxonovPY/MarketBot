import asyncio
import logging
import sys
import bcrypt

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.utils.i18n import I18n, FSMI18nMiddleware

from bot.handlera.main_handler import CustomMiddleware
from bot.handlera import dp
from utils.env_data import BotConfig
from db.model import db

TOKEN = BotConfig.TOKEN

async def on_startup(bot: Bot):
    # DB yaratish (birinchi run ichida)
    await db.init()
    await db.create_all()

    # Bot komandalarini qo‘shish
    commands = [
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/channel", description="Send channel ID"),
    ]
    await bot.set_my_commands(commands)

    # Hash parol misol (DEBUG)
    print(bcrypt.hashpw("3".encode(), salt=bcrypt.gensalt()))

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Bot va Dispatcher
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Til middleware
    i18n = I18n(path='locales', default_locale='uz', domain='messages')
    dp.update.outer_middleware(FSMI18nMiddleware(i18n))
    dp.message.outer_middleware(CustomMiddleware())

    # On startup
    await on_startup(bot)

    # Polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
