from aiogram.fsm.state import StatesGroup, State


class RegisterGroup(StatesGroup):
    age = State()
    gender = State()
    country = State()
    name = State()
