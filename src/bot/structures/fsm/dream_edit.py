from aiogram.fsm.state import StatesGroup, State


class DreamEditGroup(StatesGroup):
    name = State()
    description = State()
    image = State()
