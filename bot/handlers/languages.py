from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram.utils.i18n import I18n, gettext as _, lazy_gettext as __

from bot.buttons.reply import reply_button_builder
from bot.states import States

router = Router()


@router.message(F.text == __('🇷🇺 🇺🇿 Tillar'))
async def language_user(message: Message, state: FSMContext):
    text: list[str] = ['🇺🇿 Uzb', '🇷🇺 Rus', _('◀️ Orqaga')]
    markup: ReplyKeyboardMarkup = await reply_button_builder(text, (3, 1))
    await state.set_state(States.language)
    await message.answer(text=_('Tilni tanlang:'), reply_markup=markup)


@router.message(States.language)
async def language_handler(message: Message, state: FSMContext, i18n: I18n):
    map_lang: dict[str, str] = {
        '🇺🇿 Uzb': 'uz',
        '🇷🇺 Rus': 'ru'
    }
    code: str = map_lang.get(message.text)
    i18n.current_locale = code
    lang: str = await state.get_value('locale')
    await state.clear()
    await state.update_data({'locale': lang})
    await state.update_data(locale=code)
    text: list[str] = [_('🏬 Mahsulotlar bolimi'), _('📦 Haridlar'), _('🇷🇺 🇺🇿 Tillar'), _('📞 Aloqa')]
    markup: ReplyKeyboardMarkup = await reply_button_builder(text, (3, 1))
    await message.answer(text=_('✅ Hush kelibsiz!'), reply_markup=markup)
