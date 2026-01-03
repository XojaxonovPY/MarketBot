from bot.dispatcher import dp
from bot.handlers.admin import router as admin
from bot.handlers.languages import router as language
from bot.handlers.main_handler import router as main_router
from bot.handlers.main_section import router as main_section

dp.include_router(main_section)
dp.include_router(language)
dp.include_router(main_router)
dp.include_router(admin)
