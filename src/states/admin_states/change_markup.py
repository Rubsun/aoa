from aiogram.fsm.state import State, StatesGroup


class ChangeMarkupState(StatesGroup):
    waiting_for_new_markup = State()
