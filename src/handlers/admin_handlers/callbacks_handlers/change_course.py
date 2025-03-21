from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from db.models import ExchangeSettings
from src.handlers.admin_handlers.callbacks_handlers.router import router
from src.states.admin_states.change_course import ChangeCourseState


@router.callback_query(F.data == 'change_course')
async def change_course(callback: CallbackQuery, state: FSMContext):
    exchange_settings = ExchangeSettings.get()
    await state.set_state(ChangeCourseState.waiting_for_rub_usdt)
    await callback.message.answer('Введите новый курс USDT/RUB\n'
                                  f'Текущий курс: {exchange_settings.rub_to_usdt}')
