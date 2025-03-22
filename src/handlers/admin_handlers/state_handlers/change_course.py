from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from db.models import ExchangeSettings
from src.filters.isAdmin import IsAdmin
from src.handlers.admin_handlers.state_handlers.router import router
from src.states.admin_states.change_course import ChangeCourseState


@router.message(ChangeCourseState.waiting_for_rub_usdt, IsAdmin())
async def waiting_for_rub_usdt(message: Message, state: FSMContext):
    exchange_settings = ExchangeSettings.get()
    try:
        new_course = float(message.text.replace(',', '.'))
        exchange_settings.rub_to_usdt = new_course
        exchange_settings.save()
        await state.set_state(ChangeCourseState.waiting_for_thb_usdt)
        await message.answer(text=f'Введите новый курс THB/USDT\n'
                                  f'Текущий курс: {exchange_settings.thb_to_usdt}')
    except ValueError:
        await message.answer(text='Введите корректное число (например, 12.34)')
        return


@router.message(ChangeCourseState.waiting_for_thb_usdt, IsAdmin())
async def waiting_for_thb_usdt(message: Message, state: FSMContext):
    exchange_settings = ExchangeSettings.get()
    try:
        new_course = float(message.text.replace(',', '.'))
        exchange_settings.thb_to_usdt = new_course
        exchange_settings.save()

        txt = (f'Текущий режим работы: {exchange_settings.mode}\n'
               f'Параметры ручного режима:\n'
               f'USDT/RUB: {exchange_settings.rub_to_usdt}\n'
               f'THB/USDT: {exchange_settings.thb_to_usdt}')

        if exchange_settings.mode == 'manual':
            btn = [InlineKeyboardButton(text='Переключить на автоматический режим', callback_data='set_mode_auto')]
        else:
            btn = [InlineKeyboardButton(text='Переключить на ручной режим', callback_data='set_mode_manual')]

        kb = InlineKeyboardMarkup(inline_keyboard=[
            btn,
            [InlineKeyboardButton(text='Изменить курс ручного режима', callback_data='change_course')]
        ])

        await message.answer(text=txt, reply_markup=kb)
        await state.clear()
    except ValueError:
        await message.answer(text='Введите корректное число (например, 12.34)')
        return
