from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message
from peewee import DoesNotExist  # Импортируем исключение для проверки отсутствия записи

from db.models import User
from src.handlers.admin_handlers.state_handlers.router import router
from src.states.admin_states.cmd_user import GetUserState


@router.message(GetUserState.waiting_for_username_or_id)
async def waiting_for_username_or_id(message: Message, state: FSMContext):
    input_data = message.text.strip()

    user = None
    if input_data.isdigit():
        try:
            user = User.get((User.user_id == int(input_data)) | (User.id == int(input_data)))
        except DoesNotExist:
            user = None
    else:
        try:
            user = User.get(User.username == input_data)
        except DoesNotExist:
            user = None

    if user:
        banned_status = "Забанен" if user.banned else "Не забанен"

        if user.banned:
            buttons = InlineKeyboardButton(text='Разбанить', callback_data=f'unban_{user.user_id}')
        else:
            buttons = InlineKeyboardButton(text='Забанить', callback_data=f'ban_{user.user_id}')

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[buttons]])

        await message.answer(
            f"Статус пользователя @{user.username} ({user.user_id}):\n{banned_status}",
            reply_markup=keyboard
        )
    else:
        await message.answer("Пользователь не найден. Пожалуйста, попробуйте снова.")
