from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from db.models import ExchangeSettings
from src.filters.isAdmin import IsAdmin
from src.handlers.admin_handlers.state_handlers.router import router
from src.states.admin_states.change_markup import ChangeMarkupState


@router.message(ChangeMarkupState.waiting_for_new_markup, IsAdmin())
async def waiting_for_new_markup(message: Message, state: FSMContext):
    new_markup = message.text
    settings = ExchangeSettings.get()

    settings.markup_percentage = new_markup
    settings.save()

    txt = f'Текущая наценка: {settings.markup_percentage}%'
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить процент', callback_data='change_markup')]
    ])
    await state.clear()
    await message.answer(txt, reply_markup=kb)