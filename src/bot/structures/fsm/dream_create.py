from aiogram.fsm.state import StatesGroup, State


class DreamGroup(StatesGroup):
    name = State()
    description = State()
    image = State()
