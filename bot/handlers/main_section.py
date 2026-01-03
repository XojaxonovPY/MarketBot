from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineQuery, InlineQueryResultArticle
from aiogram.types import InlineKeyboardButton, InputTextMessageContent
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram.utils.i18n import gettext as _

from bot.buttons.inline import build_inline_buttons
from bot.buttons.reply import reply_button_builder
from db.models import Product, Order
from utils.env_data import BotConfig

router = Router()
PAYMENT_CLICK_TOKEN = BotConfig.PAYMENT_CLICK_TOKEN


@router.callback_query(F.data.startswith("category_"))
async def category_handler(callback: CallbackQuery):
    category_id = int(callback.data.split('_')[1])
    products: list[Product] = await Product.filter_(Product.category_id == category_id)
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=i.name, callback_data=f'product_{i.id}')
        for i in products
    ]
    markup: InlineKeyboardMarkup = await build_inline_buttons(buttons, [2] * (len(buttons) // 2))
    await callback.message.answer(text=_('✅ Mahsulotlarni tanlang:'), reply_markup=markup)


@router.callback_query(F.data.startswith("product_"))
async def product_handler(callback: CallbackQuery, state: FSMContext):
    product_id: int = int(callback.data.split('_')[1])
    product: Product = await Product.get(id=product_id)
    caption: str = f'Nomi:{product.name}\nNarxi:{product.price}\nSoni:{product.count}'
    await state.update_data(product=product)
    await callback.message.answer_photo(photo=product.image_url, caption=caption)
    quantity = product.count + 1 if product.count <= 10 else 11
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=str(i), callback_data=f'count_{i}')
        for i in range(1, quantity)
    ]
    markup: InlineKeyboardMarkup = await build_inline_buttons(buttons, [8] * (len(buttons) // 2))
    await callback.message.answer(text=_('✅ Qancha olmoqchisiz:'), reply_markup=markup)


@router.callback_query(F.data.startswith("count_"))
async def order_handler(callback: CallbackQuery, state: FSMContext):
    quantity: int = int(callback.data.split('_')[1])
    data: dict = await state.get_data()
    product: Product = data.get('product')
    markup: ReplyKeyboardMarkup = await reply_button_builder([_('◀️Mahsulotlarga')])
    amount: int = int(product.price * 100)
    total_price: int = amount * quantity
    prices: list[LabeledPrice] = [
        LabeledPrice(label=product.name, amount=total_price),
    ]
    await state.update_data(total_price=total_price, quantity=quantity)
    await callback.message.answer(text=_('✅ Yana mahsulot harit qilasizmi!'), reply_markup=markup)
    await callback.message.answer_invoice('Products', f"Jami {quantity} mahsulot sotib  qilindi", f'{product.id}',
                                          "UZS", prices, PAYMENT_CLICK_TOKEN)


@router.pre_checkout_query()
async def success_handler(pre_checkout_query: PreCheckoutQuery) -> None:
    await pre_checkout_query.answer(True)


@router.message(lambda message: bool(message.successful_payment))
async def confirm_handler(message: Message, state: FSMContext):
    user_id: int = message.chat.id
    data: dict = await state.get_data()
    product = data.get('product')
    if message.successful_payment:
        order = {
            'product_id': product.id,
            'quantity': data.get('quantity'),
            'total_price': data.get('total_price'),
            'user_id': user_id,
        }
        order_obj: Order = await Order.create(**order)
        await Product.sub_product(product.id, order_obj.quantity)
        lang: str = await state.get_value('locale')
        await state.clear()
        await state.update_data(locale=lang)
        await message.answer(text=_(f"✅ To'lo'vingiz uchun raxmat 😊 \n{order_obj.total_price}\n{order_obj.id}"))


# ================================================Searching============================================

@router.inline_query()
async def inline_query(inline: InlineQuery):
    query: str = inline.query.lower()
    result: list = []
    products: list[Product] = await Product.all_()
    for product in products:
        if query in product.name.lower():
            i = InlineQueryResultArticle(
                id=str(f'👤{product.id}'),
                title=product.name,
                description=str(f'Narxi:{product.price}\n Soni:{product.count}'),
                thumbnail_url=product.thumbnail_url,
                input_message_content=InputTextMessageContent(message_text=str(product.id)),
            )
            result.append(i)
    await inline.answer(result, cache_time=5, is_personal=True)


@router.message(F.via_bot)
async def any_text(message: Message, state: FSMContext):
    product_id = int(message.text)
    await message.delete()
    product: Product = await Product.get(id=product_id)
    caption: str = f'Nomi:{product.name}\nNarxi:{product.price}\nSoni:{product.count}'
    await message.answer_photo(photo=product.image_url, caption=caption)
    quantity: int = product.count + 1 if product.count <= 10 else 11
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=str(i), callback_data=f'count_{i}')
        for i in range(1, quantity)
    ]
    markup: InlineKeyboardMarkup = await build_inline_buttons(buttons, [8] * (len(buttons) // 2))
    await state.update_data(product=product)
    await message.answer(text=_('✅ Qancha olmoqchisiz:'), reply_markup=markup)
