from bot.dispatcher import dp
from bot.handlers.main_section import main_section
from bot.handlers.languages import language
from bot.handlers.main_handler import main_router
from bot.handlers.admin import admin

dp.include_routers(
    *[main_router,
      language,
      main_section,
      admin
    ]
)