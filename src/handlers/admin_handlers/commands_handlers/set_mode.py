from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from db.models import ExchangeSettings
from src.filters.isAdmin import IsAdmin
from src.handlers.admin_handlers.commands_handlers.router import router


@router.message(Command('set_mode'), IsAdmin())
async def cmd_set_mode(message: Message):
    exchange_settings = ExchangeSettings.get()

    if exchange_settings.mode == 'manual':
        btn = [InlineKeyboardButton(text='Переключить на автоматический режим', callback_data='set_mode_auto')]
    else:
        btn = [InlineKeyboardButton(text='Переключить на ручной режим', callback_data='set_mode_manual')]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        btn,
        [InlineKeyboardButton(text='Изменить курс ручного режима', callback_data='change_course')]
    ])

    txt = (f'Текущий режим работы: {exchange_settings.mode}\n'
           f'Параметры ручного режима:\n'
           f'USDT/RUB: {exchange_settings.rub_to_usdt}\n'
           f'THB/USDT: {exchange_settings.thb_to_usdt}')

    await message.answer(text=txt, reply_markup=kb)
