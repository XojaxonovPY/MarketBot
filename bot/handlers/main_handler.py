import asyncio

from aiogram import F, BaseMiddleware
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from bot.buttons.inline import build_inline_buttons
from bot.buttons.reply import reply_button_builder
from db.models import Category, Channel, Order, User

router = Router()


@router.message(CommandStart())
async def command_handler(message: Message):
    user: dict = {
        'user_id': message.from_user.id,
        'username': message.from_user.username
    }
    await User.save_user(user)
    text: list[str] = [_('🏬 Mahsulotlar bolimi'), _('📦 Haridlar'), _('🇷🇺 🇺🇿 Tillar'), _('📞 Aloqa')]
    markup: ReplyKeyboardMarkup = await reply_button_builder(text, (3, 1))
    await message.answer(text=_('✅ Hush kelibsiz!'), reply_markup=markup)


@router.message(F.text == __('📦 Haridlar'))
async def order_list(message: Message):
    user_id: int = message.chat.id
    orders: list[Order] = await Order.filter_(Order.user_id == user_id)
    if not orders:
        await message.answer(text='✅ Hozircha haridlar amalga oshirilmagan!')
    for i in orders:
        caption: str = f'Nomi:{i.product.name}\nNarxi:{i.product.price}\nSoni:{i.quantity},Jami narx:{i.total_price}'
        await message.answer_photo(photo=i.product.image_url, caption=caption)


@router.message(F.text == __('🏬 Mahsulotlar bolimi'))
@router.message(F.text == __('◀️Mahsulotlarga'))
async def main_handler(message: Message):
    categories: list[Category] = await Category.all_()
    text: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}")
        for category in categories
    ]
    markup: InlineKeyboardMarkup = await build_inline_buttons(text, [2] * (len(categories) // 2))
    text2: list[InlineKeyboardButton] = [InlineKeyboardButton(text=_('🔎Qidiruv'), switch_inline_query_current_chat='')]
    markup2: InlineKeyboardMarkup = await build_inline_buttons(text2)
    await message.answer(text=_('🔎 Mahsulotlar qidiruvi'), reply_markup=markup2)
    await message.answer(text=_('✅ Asosiy bolim:'), reply_markup=markup)


@router.message(F.text == __('📞 Aloqa'))
async def com_handler(message: Message):
    await message.answer(text='+998992771281')


@router.message(F.photo)
async def image_handler(message: Message):
    file_id: str = message.photo[-1].file_id
    await message.answer(text=file_id)


# @router.message()
# async def write(message: Message):
#
#     id=message.forward_from_chat.id
#     with open('tel.txt', 'a') as f:
#         f.write(str(id))


@router.message(Command('ad'))
async def ad_command_handler(message: Message):
    tasks: list = []
    users: list[User] = await User.all_()
    for i in range(100):
        for u in users:
            tasks.append(message.bot.send_message(u.user_id, text=f"Reklama {i}"))
            if len(tasks) >= 25:
                await asyncio.gather(*tasks)
                tasks = []
                await asyncio.sleep(1)


# =====================================================Subscribe in channels===========================
class CustomMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        user_id: int = event.chat.id
        channels: list[Channel] = await Channel.all_()
        not_join_channels: list = []
        if channels:
            for channel in channels:
                response = await data.get('bot').get_chat_member(channel.channel_id, user_id)
                if not response.status in ["member", "creator", 'admin']:
                    not_join_channels.append(channel)
        if not_join_channels:
            buttons: list[InlineKeyboardButton] = [
                InlineKeyboardButton(text=channel.name, url=channel.link)
                for channel in not_join_channels
            ]
            markup: InlineKeyboardMarkup = await build_inline_buttons(buttons)
            await data.get('bot').send_message(user_id, _("✅ Quydagi kannalarga obuna bo'l"), reply_markup=markup)
        else:
            return await handler(event, data)
