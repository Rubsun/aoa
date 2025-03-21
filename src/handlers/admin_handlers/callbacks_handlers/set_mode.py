from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from db.models import ExchangeSettings
from src.handlers.admin_handlers.callbacks_handlers.router import router


@router.callback_query(F.data.startswith(f'set_mode_'))
async def change_mode(callback: CallbackQuery):
    mode = callback.data.split('_')[2]
    exchange_settings = ExchangeSettings.get()
    exchange_settings.mode = mode
    exchange_settings.save()
    if mode == 'manual':
        btn = [InlineKeyboardButton(text='Переключить на автоматический режим', callback_data='set_mode_auto')]
    else:
        btn = [InlineKeyboardButton(text='Переключить на ручной режим', callback_data='set_mode_manual')]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        btn,
        [InlineKeyboardButton(text='Изменить курс ручного режима', callback_data='set_course')]
    ])

    txt = (f'Текущий режим работы: {exchange_settings.mode}\n'
           f'Параметры ручного режима:\n'
           f'USDT/RUB: {exchange_settings.rub_to_usdt}\n'
           f'THB/USDT: {exchange_settings.thb_to_usdt}')

    await callback.message.edit_text(text=txt, reply_markup=kb)
