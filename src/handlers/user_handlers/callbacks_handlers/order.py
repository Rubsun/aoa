from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from src.handlers.user_handlers.callbacks_handlers.router import router
from src.states.user_states.choose_course import ChooseCourseState


@router.callback_query(F.data == 'create_order')
async def create_order(callback: CallbackQuery):
    txt = 'Выберите расчет, который хотите получить 👇'
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='В рублях', callback_data='choose_RUB'),
            InlineKeyboardButton(text='В батах', callback_data='choose_THB'),
            InlineKeyboardButton(text='В USDT', callback_data='choose_USDT'),
        ]
    ])

    await callback.message.answer(txt, reply_markup=kb)


@router.callback_query(F.data.startswith('choose_'))
async def choose_course(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[1]

    await state.update_data(currency=currency)

    await state.set_state(ChooseCourseState.waiting_for_amount)
    await callback.message.edit_text("Введите сумму, которую хотите обменять:")
