import asyncio
import logging
import sys
import threading

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from starlette_admin.contrib.sqla import Admin, ModelView

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.utils.i18n import I18n, FSMI18nMiddleware

from bot.handlers import dp
from bot.handlers.main_handler import CustomMiddleware
from utils.env_data import BotConfig
from db import db
from db.model import metadata, User, Product, Category, Order, Channel
from web.provider import UsernameAndPasswordProvider


TOKEN = BotConfig.TOKEN


# ============= Aiogram setup =============
async def init_models():
    async with db._engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start bot"),
        BotCommand(command="channel", description="Send channel id"),
    ]
    await bot.set_my_commands(commands)


async def start_bot():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Middlewares
    dp.message.outer_middleware(CustomMiddleware())
    i18n = I18n(path='locales', default_locale='uz', domain='messages')
    dp.update.outer_middleware(FSMI18nMiddleware(i18n))

    await init_models()
    await set_bot_commands(bot)
    await dp.start_polling(bot)


def run_bot():
    asyncio.run(start_bot())


# ============= Starlette Admin setup =============
app = Starlette(
    debug=True,
    middleware=[
        Middleware(SessionMiddleware, secret_key="sdgfhjhhsfdghn")
    ],
    routes=[
        Route("/", lambda request: PlainTextResponse("✅ Bot va Admin panel ishga tushdi")),
    ],
)

admin = Admin(
    db._engine,
    title="P_29Admin",
    base_url="/admin",
    auth_provider=UsernameAndPasswordProvider(),
)
admin.add_view(ModelView(User))
admin.add_view(ModelView(Category))
admin.add_view(ModelView(Product))
admin.add_view(ModelView(Order))
admin.add_view(ModelView(Channel))
admin.mount_to(app)
# ============= Start both together =============
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    threading.Thread(target=run_bot, daemon=True).start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
