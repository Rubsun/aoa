from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.filters.isAdmin import IsAdmin
from src.handlers.admin_handlers.callbacks_handlers.router import router
from src.states.admin_states.change_markup import ChangeMarkupState


@router.callback_query(F.data == 'change_markup', IsAdmin())
async def change_markup(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeMarkupState.waiting_for_new_markup)
    await callback_query.message.edit_text(text='Введите новый процент наценки')
