from aiogram.fsm.state import StatesGroup,State
class States(StatesGroup):
  language=State()
  admin=State()