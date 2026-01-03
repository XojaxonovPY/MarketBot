from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def build_inline_buttons(buttons: list[InlineKeyboardButton], size=(1,)) -> InlineKeyboardMarkup:
    rkb = InlineKeyboardBuilder()
    rkb.add(*buttons)
    rkb.adjust(*size)
    return rkb.as_markup()
