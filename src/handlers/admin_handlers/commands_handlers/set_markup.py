from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from db.models import ExchangeSettings
from src.filters.isAdmin import IsAdmin
from src.handlers.admin_handlers.commands_handlers.router import router


@router.message(Command("set_markup"), IsAdmin())
async def set_markup(message: Message, state: FSMContext):
    settings = ExchangeSettings.get()
    txt = f'Текущая наценка: {settings.markup_percentage}%'
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить процент', callback_data='change_markup')]
    ])

    await message.answer(txt, reply_markup=kb)
    # try:
    #     new_markup = float(message.text.split()[1])
    #     settings = ExchangeSettings.get()
    #     settings.markup_percentage = Decimal(new_markup)
    #     settings.save()
    #     await message.answer(f"Наценка успешно изменена на {new_markup}%")
    # except:
    #     await message.answer("Использование: /set_markup <процент>")
