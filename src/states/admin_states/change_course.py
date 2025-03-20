from aiogram.fsm.state import State, StatesGroup


class ChangeCourseState(StatesGroup):
    waiting_for_rub_usdt = State()
    waiting_for_thb_usdt = State()
