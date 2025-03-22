import asyncio
import time
from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware, types
from peewee import DoesNotExist

from db.models import User


class BanMiddleware(BaseMiddleware):
    def __init__(self):
        self.cache = {}
        self.ttl = 300

    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        message = None
        print(self.cache)
        if isinstance(event, types.Update):
            message = event.message or event.callback_query or event.edited_message

        if not isinstance(message, (types.Message, types.CallbackQuery)) or not message.from_user:
            return await handler(event, data)

        user_id = message.from_user.id

        cached = self.cache.get(user_id)
        if cached:
            timestamp, banned = cached
            if time.time() - timestamp <= self.ttl:
                if banned:
                    await self._send_ban_message(message, data)
                    return
                return await handler(event, data)
            else:
                del self.cache[user_id]

        try:
            user = await asyncio.to_thread(User.get, User.user_id == user_id)
        except DoesNotExist:
            self.cache[user_id] = (time.time(), False)
            return await handler(event, data)
        except Exception:
            return await handler(event, data)

        self.cache[user_id] = (time.time(), user.banned)

        if user.banned:
            await self._send_ban_message(message, data)
            return

        return await handler(event, data)

    @staticmethod
    async def _send_ban_message(event: types.Message | types.CallbackQuery, data: dict):
        bot = data.get("bot")
        if not bot:
            return
        try:
            await bot.send_message(
                chat_id=event.from_user.id,
                text="🚫 Вы забанены и не можете использовать бота"
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения о бане: {e}")
