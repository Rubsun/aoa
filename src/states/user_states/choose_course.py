from aiogram.fsm.state import State, StatesGroup


class ChooseCourseState(StatesGroup):
    waiting_for_amount = State()
