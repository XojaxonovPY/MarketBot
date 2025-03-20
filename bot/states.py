from aiogram.fsm.state import StatesGroup,State
class States(StatesGroup):
  language=State()
  products=State()
  orders=State()
  count=State()