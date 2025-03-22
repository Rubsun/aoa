from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from config.settings import settings


class IsAdmin(BaseFilter):
    async def __call__(self, obj, *args, **kwargs):
        user_id = obj.from_user.id
        chat_id = settings.ADMIN_CHAT_ID

        try:
            member = await obj.bot.get_chat_member(chat_id, user_id)
            return member.status in ('member', 'administrator', 'creator')
        except Exception:
            return False