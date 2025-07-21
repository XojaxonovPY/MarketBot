import asyncio

from aiogram import F, BaseMiddleware
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton
from aiogram import Router
from bot.buttons.inline import build_inline_buttons
from bot.buttons.reply import reply_button_builder
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from db.model import Category, Channel, Order, User

main_router = Router()


@main_router.message(CommandStart())
async def command_handler(message: Message):
    users = {
        'user_id': message.from_user.id,
        'username': message.from_user.username
    }
    await User.save_user(**users)
    text = [_('🏬 Mahsulotlar bolimi'), _('📦 Haridlar'), _('🇷🇺 🇺🇿 Tillar'), _('📞 Aloqa')]
    markup = await reply_button_builder(text, (3, 1))
    await message.answer(text=_('✅ Hush kelibsiz!'), reply_markup=markup)


@main_router.message(F.text == __('📦 Haridlar'))
async def order_list(message: Message):
    user_id = message.chat.id
    orders: list[Order] = await Order.gets(Order.user_id, user_id)
    if not orders:
        await message.answer(text='✅ Hozircha haridlar amalga oshirilmagan!')
    for i in orders:
        caption = f'Nomi:{i.product.name}\nNarxi:{i.product.price}\nSoni:{i.quantity},Jami narx:{i.total_price}'
        await message.answer_photo(photo=i.product.image_url, caption=caption)


@main_router.message(F.text == __('🏬 Mahsulotlar bolimi'))
@main_router.message(F.text == __('◀️Mahsulotlarga'))
async def main_handler(message: Message):
    categories: list = await Category.get_all()
    text = [InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}") for category in
            categories]
    markup = await build_inline_buttons(text, [2] * (len(categories) // 2))
    text2 = [InlineKeyboardButton(text=_('🔎Qidiruv'), switch_inline_query_current_chat='')]
    markup2 = await build_inline_buttons(text2)
    await message.answer(text=_('🔎 Mahsulotlar qidiruvi'), reply_markup=markup2)
    await message.answer(text=_('✅ Asosiy bolim:'), reply_markup=markup)


@main_router.message(F.text == __('📞 Aloqa'))
async def com_handler(message: Message):
    await message.answer(text='+998992771281')


@main_router.message(F.photo)
async def image_handler(message: Message):
    file_id = message.photo[-1].file_id
    await message.answer(text=file_id)


# @main_router.message()
# async def write(message: Message):
#
#     id=message.forward_from_chat.id
#     with open('tel.txt', 'a') as f:
#         f.write(str(id))


@main_router.message(Command('ad'))
async def ad_command_handler(message: Message):
    tasks = []
    users: list[User] = await User.get_all()
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
        user_id = event.chat.id
        channels: list[Channel] = await Channel.get_all()
        not_join_channels = []
        if channels:
            for channel in channels:
                response = await data.get('bot').get_chat_member(channel.channel_id, user_id)
                if not response.status in ["member", "creator", 'admin']:
                    not_join_channels.append(channel)
        if not_join_channels:
            buttons = [InlineKeyboardButton(text=channel.name, url=channel.link) for channel in not_join_channels]
            markup = await build_inline_buttons(buttons)
            await data.get('bot').send_message(user_id, _("✅ Quydagi kannalarga obuna bo'l"), reply_markup=markup)
        else:
            return await handler(event, data)
