from bot.dispatcher import dp
from bot.handlera.main_section import main_section
from bot.handlera.languages import language
from bot.handlera.main_handler import main_router
from bot.handlera.admin import admin

dp.include_routers(
    *[main_router,
      language,
      main_section,
      admin
    ]
)