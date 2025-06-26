from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineQuery, InlineQueryResultArticle
from aiogram.types import InlineKeyboardButton, InputTextMessageContent
from aiogram import Router
from bot.buttons.inline import build_inline_buttons
from bot.buttons.reply import reply_button_builder
from aiogram.utils.i18n import gettext as _
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from db.model import Product, Order
from utils.env_data import BotConfig

main_section = Router()
PAYMENT_CLICK_TOKEN = BotConfig.PAYMENT_CLICK_TOKEN


@main_section.callback_query(F.data.startswith("category_"))
async def category_handler(callback: CallbackQuery):
    category_id = int(callback.data.split('_')[1])
    products: list[Product] = await Product.gets(Product.category_id, category_id)
    buttons = [InlineKeyboardButton(text=i.name, callback_data=f'product_{i.id}') for i in products]
    markup = await build_inline_buttons(buttons, [2] * (len(buttons) // 2))
    await callback.message.answer(text=_('✅ Mahsulotlarni tanlang:'), reply_markup=markup)


@main_section.callback_query(F.data.startswith("product_"))
async def product_handler(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split('_')[1])
    product: Product = await Product.get(Product.id, product_id)
    caption = f'Nomi:{product.name}\nNarxi:{product.price}\nSoni:{product.count}'
    await state.update_data(product=product)
    await callback.message.answer_photo(photo=product.image_url, caption=caption)
    quantity = product.count + 1 if product.count <= 10 else 11
    buttons = [InlineKeyboardButton(text=str(i), callback_data=f'count_{i}') for i in range(1, quantity)]
    markup = await build_inline_buttons(buttons, [8] * (len(buttons) // 2))
    await callback.message.answer(text=_('✅ Qancha olmoqchisiz:'), reply_markup=markup)


@main_section.callback_query(F.data.startswith("count_"))
async def order_handler(callback: CallbackQuery, state: FSMContext):
    quantity = int(callback.data.split('_')[1])
    data = await state.get_data()
    product: Product = data.get('product')
    markup = await reply_button_builder([_('◀️Mahsulotlarga')])
    prices = [
        {
            'id': product.id,
            'name': product.name,
            'price': product.price,
        }
    ]
    amount = int(product.price * 100)
    total_price = amount * quantity
    prices = [
        LabeledPrice(label=product.name, amount=total_price),
    ]
    await state.update_data(total_price=total_price, quantity=quantity)
    await callback.message.answer(text=_('✅ Yana mahsulot harit qilasizmi!'), reply_markup=markup)
    await callback.message.answer_invoice('Products', f"Jami {quantity} mahsulot sotib  qilindi", f'{product.id}',
                                          "UZS", prices, PAYMENT_CLICK_TOKEN)


@main_section.pre_checkout_query()
async def success_handler(pre_checkout_query: PreCheckoutQuery) -> None:
    await pre_checkout_query.answer(True)


@main_section.message(lambda message: bool(message.successful_payment))
async def confirm_handler(message: Message, state: FSMContext):
    user_id = message.chat.id
    data = await state.get_data()
    product = data.get('product')
    if message.successful_payment:
        total_amount = message.successful_payment.total_amount // 100
        order_id = int(message.successful_payment.invoice_payload)
        order = {
            'product_id': product.id,
            'quantity': data.get('quantity'),
            'total_price': data.get('total_price'),
            'user_id': user_id,
        }
        await Order.create(**order)
        await state.clear()
        await message.answer(text=_(f"✅ To'lo'vingiz uchun raxmat 😊 \n{total_amount}\n{order_id}"))


# ================================================Searching============================================

@main_section.inline_query()
async def inline_query(inline: InlineQuery):
    query = inline.query.lower()
    result = []
    products: list[Product] = await  Product.get_all()
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


@main_section.message(F.via_bot)
async def any_text(message: Message):
    product_id = int(message.text)
    await message.delete()
    product: Product = await Product.get(Product.id, product_id)
    caption = f'Nomi:{product.name}\nNarxi:{product.price}\nSoni:{product.count}'
    await message.answer_photo(photo=product.image_url, caption=caption)
