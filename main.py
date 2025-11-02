import asyncio
import logging
import sys
import uvicorn

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.utils.i18n import I18n, FSMI18nMiddleware
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin, ModelView
from web.provider import UsernameAndPasswordProvider
from db.model import db, User, Product, Category, Order, Channel
from utils.env_data import BotConfig
from bot.handlers import dp
from bot.handlers.main_handler import CustomMiddleware

TOKEN = BotConfig.TOKEN

# --- Starlette Admin ---
app = Starlette()
admin = Admin(
    db._engine,
    title='P_29Admin',
    base_url='/',
    auth_provider=UsernameAndPasswordProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key="supersecret")]
)
admin.add_view(ModelView(User))
admin.add_view(ModelView(Category))
admin.add_view(ModelView(Product))
admin.add_view(ModelView(Order))
admin.add_view(ModelView(Channel))
admin.mount_to(app)


async def init_models():
    async with db._engine.begin() as conn:
        await conn.run_sync(db.Base.metadata.create_all)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Start bot"),
        BotCommand(command="/channel", description="Send channel id"),
    ]
    await bot.set_my_commands(commands=commands)


async def start_bot():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    i18n = I18n(path='locales', default_locale='uz', domain='messages')
    dp.update.outer_middleware(FSMI18nMiddleware(i18n))
    dp.message.outer_middleware(CustomMiddleware())
    await set_bot_commands(bot)
    await init_models()

    # 👇 Muhim: signal handler'ni o‘chirib qo‘yamiz
    await dp.start_polling(bot, handle_signals=False)


async def main():
    # ikkita taskni parallel ishga tushiramiz
    server_task = asyncio.create_task(
        uvicorn.Server(
            uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        ).serve()
    )
    bot_task = asyncio.create_task(start_bot())

    await asyncio.gather(server_task, bot_task)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
