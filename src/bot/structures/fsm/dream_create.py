from aiogram.fsm.state import StatesGroup, State


class DreamGroup(StatesGroup):
    name = State()
    category = State()  # Новое состояние для выбора категории
    description = State()
    image = State()
