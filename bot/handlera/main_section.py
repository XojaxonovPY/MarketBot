from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram import Router
from bot.buttons.reply import reply_button_builder
from aiogram.utils.i18n import gettext as _
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery

from db.model import Product
from utils.env_data import BotConfig
from bot.functions import get_products, get_orders, orders_save, search_products
from bot.states import States


main_section=Router()
PAYMENT_CLICK_TOKEN = BotConfig.PAYMENT_CLICK_TOKEN


@main_section.callback_query(F.data.startswith("category_"))
async def category_handler(callback : CallbackQuery,state:FSMContext):
    call=callback.data
    product=await get_products(call)
    product.append('◀️Mahsulotlarga')
    markup=await reply_button_builder(product,[2]*(len(product) // 2))
    await state.update_data(product=product)
    await state.set_state(States.products)
    await callback.message.answer(text=_('✅ Mahsulotlarni tanlang:'),reply_markup=markup)


@main_section.message(States.products)
async def product_handler(message:Message,state:FSMContext):
    product=message.text
    data=await state.get_data()
    check_product=data.get('product')
    if product not in check_product:
        await message.answer(text=_('✅ Bunday mahsulot bizda yoq!'))
        return
    price,count,image,id_=await get_orders(product)
    await state.update_data(price=price,count=count,product_name=product,product_id=id_)
    await message.answer_photo(photo=image,caption=f'narxi:{price}\nsoni:{count}')
    await state.set_state(States.orders)
    await message.answer(text=_('✅ Nechta olmoqchisiz:'))


@main_section.message(States.orders)
async def order_handler(message: Message, state: FSMContext):
    quantity = message.text.strip()
    data = await state.get_data()
    id_ = data.get('product_id')
    name = data.get('product_name')
    price = data.get('price')
    count = data.get('count')
    count = int(count)
    price = float(price)
    markup = await reply_button_builder([_('◀️Mahsulotlarga')])
    if not quantity.isdigit():
        await message.answer(text=_('❌ Iltimos, mahsulot sonini butun son shaklida kiriting!'),reply_markup=markup)
        return
    quantity = int(quantity)
    if quantity > count:
        await message.answer(text=_('❌ Buncha mahsulot bizda yo‘q!'),reply_markup=markup)
        return
    prices=[
        {
            'id':id_,
            'name':name,
            'price': price
        }
    ]
    amount = int(price*quantity * 100)
    prices = [
        LabeledPrice(label=name, amount=amount*quantity),
    ]
    await message.answer(text=_('✅ Yana mahsulot harit qilasizmi!'),reply_markup=markup)
    await message.answer_invoice('Products', f"Jami {quantity} mahsulot sotib  qilindi",
                                '1',"UZS",prices, PAYMENT_CLICK_TOKEN)


@main_section.pre_checkout_query()
async def success_handler(pre_checkout_query: PreCheckoutQuery) -> None:
    await pre_checkout_query.answer(True)


@main_section.message(lambda message: bool(message.successful_payment))
async def confirm_handler(message: Message, state: FSMContext):
    user_id = message.chat.id
    data=await state.get_data()
    product_id = data.get('product_id')
    product_name = data.get('product_name')
    product_price = data.get('price')
    product_count = data.get('count')
    product_price = float(product_price)
    product_count = int(product_count)
    if message.successful_payment:
        total_amount = message.successful_payment.total_amount//100
        order_id = int(message.successful_payment.invoice_payload)
        order = {
            'product_id': product_id,
            'product_name': product_name,
            'product_price': product_price,
            'product_count': product_count,
            'user_id': user_id,
        }
        await orders_save(**order)
        await state.clear()
        await message.answer(text=_(f"✅ To'lo'vingiz uchun raxmat 😊 \n{total_amount}\n{order_id}"))

# ================================================Searching============================================

@main_section.inline_query()
async def inline_query(inline: InlineQuery):
    query = inline.query.lower()
    result = []
    products: list = await  Product.get_all()
    for product in products:
        if query in product.name.lower():
            i = InlineQueryResultArticle(
                id=str(f'👤{product.id}'),
                title=product.name,
                description=str(f'narxi:{product.price}\n soni:{product.count}'),
                input_message_content=InputTextMessageContent(message_text=str(product.id)),
            )
            result.append(i)
    await inline.answer(result, cache_time=5, is_personal=True)


@main_section.message(F.via_bot)
async def any_text(message: Message):
    product_id = int(message.text)
    await message.delete()
    product_name,product_price,product_count,image=await search_products(product_id)
    await message.answer_photo(photo=image,caption=f'Nomi:{product_name}\n'
                                                   f'Narxi:{product_price}\nSoni:{product_count}')