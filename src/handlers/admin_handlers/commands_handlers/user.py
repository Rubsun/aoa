from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.filters.isAdmin import IsAdmin
from src.handlers.admin_handlers.commands_handlers.router import router
from src.states.admin_states.cmd_user import GetUserState


@router.message(Command("user"), IsAdmin())
async def cmd_user(message: Message, state: FSMContext):
    await state.set_state(GetUserState.waiting_for_username_or_id)
    await message.answer('Введите Username или ID пользователя')
