from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from db.models import User
from src.handlers.admin_handlers.callbacks_handlers.router import router


@router.callback_query(F.data.startswith('ban_'))
async def ban_user(callback: CallbackQuery):
    user_id = callback.data.split("_")[1]
    user = User.get(user_id=user_id)
    if user:
        user.banned = True
        user.save()

        banned_status = "Забанен"
        buttons = InlineKeyboardButton(text='Разбанить', callback_data=f'unban_{user_id}')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[buttons]])

        await callback.message.edit_text(
            f"Статус пользователя @{user.username} ({user.user_id}):\n{banned_status}",
            reply_markup=keyboard
        )

        await callback.answer("Пользователь забанен")

    else:
        await callback.message.answer('Пользователь не найден')


@router.callback_query(F.data.startswith('unban_'))
async def unban_user(callback: CallbackQuery):
    user_id = callback.data.split("_")[1]
    user = User.get(user_id=user_id)
    if user:
        user.banned = False
        user.save()

        banned_status = "Не забанен"
        buttons = InlineKeyboardButton(text='Забанить', callback_data=f'ban_{user_id}')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[buttons]])

        await callback.message.edit_text(
            f"Статус пользователя @{user.username} ({user.user_id}):\n{banned_status}",
            reply_markup=keyboard
        )

        await callback.answer("Пользователь разбанен")

    else:
        await callback.message.answer('Пользователь не найден')
