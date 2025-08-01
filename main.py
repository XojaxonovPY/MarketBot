import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.utils.i18n import I18n, FSMI18nMiddleware

from bot.handlers import *
from bot.handlers.main_handler import CustomMiddleware
from utils.env_data import BotConfig
from db import db
from db.model import metadata

TOKEN = BotConfig.TOKEN


async def init_models():
    async with db._engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Starting bot."),
        BotCommand(command="/channel", description="Send channel id."),
    ]
    await bot.set_my_commands(commands=commands)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    i18n = I18n(path='locales', default_locale='uz', domain='messages')
    dp.update.outer_middleware(FSMI18nMiddleware(i18n))
    dp.message.outer_middleware(CustomMiddleware())
    await set_bot_commands(bot)
    await init_models()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
