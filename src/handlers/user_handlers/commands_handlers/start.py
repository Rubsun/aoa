from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message

from db.models import User
from src.handlers.user_handlers.commands_handlers.router import router


@router.message(CommandStart())
async def cmd_start(message: Message):
    user, created = User.get_or_create(
        user_id=message.from_user.id,
        defaults={'username': message.from_user.username, 'chat_id': message.chat.id}
    )

    txt = 'Что вы хотите сделать?'

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сделать расчет', callback_data='create_order')],
        [InlineKeyboardButton(text='Связаться с оператором', callback_data='contact_operator')],
        [InlineKeyboardButton(text='Подробнее о нас', callback_data='about')],
        [InlineKeyboardButton(text='Способы получения', callback_data='methods_obtaining')],
    ])

    await message.answer(txt, reply_markup=kb)
