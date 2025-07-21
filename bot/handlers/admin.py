import asyncio
from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from bot.states import States
from db.model import User

admin = Router()


@admin.message(F.photo)
async def image_handler(message: Message):
    file_id = message.photo[-1].file_id
    await message.answer(text=file_id)


@admin.message(Command('send'))
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


@admin.message(Command('channel'))
async def ad_command_handler(message: Message, state: FSMContext):
    await state.set_state(States.admin)
    await message.answer(text=_('Kanaldni biror habarini yuboring va kanalga botni admin qiling!'))


@admin.message(States.admin)
async def write(message: Message, state: FSMContext):
    id = message.forward_from_chat.id
    await message.answer(text=f'Kanalni idsi: {id}')
    await state.clear()
