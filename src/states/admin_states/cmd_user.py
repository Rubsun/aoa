from aiogram.fsm.state import State, StatesGroup


class GetUserState(StatesGroup):
    waiting_for_username_or_id = State()
