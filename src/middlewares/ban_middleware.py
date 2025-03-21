# from aiogram import BaseMiddleware, types
# from peewee import DoesNotExist
# import asyncio
# import time
# from typing import Any, Callable, Dict, Awaitable
#
# from db.models import User
#
#
# class BanMiddleware(BaseMiddleware):
#     def __init__(self):
#         self.cache = {}  # {user_id: (timestamp, banned_status)}
#         self.ttl = 300  # 5 минут кэширования
#
#     async def __call__(
#             self,
#             handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
#             event: types.TelegramObject,
#             data: Dict[str, Any],
#     ) -> Any:
#         # Пропускаем события без пользователя
#         if not hasattr(event, "from_user"):
#             return await handler(event, data)
#
#         user_id = event.from_user.id
#
#         # Проверка кэша
#         cached = self.cache.get(user_id)
#         if cached:
#             timestamp, banned = cached
#             if time.time() - timestamp <= self.ttl:
#                 if banned:
#                     await self._send_ban_message(event, data)
#                     return
#                 return await handler(event, data)
#             else:
#                 del self.cache[user_id]
#
#         try:
#             # Асинхронный запрос к БД через отдельный поток
#             user = await asyncio.to_thread(
#                 User.get,
#                 User.user_id == user_id
#             )
#         except DoesNotExist:
#             # Пользователя нет в БД - кэшируем как не забаненного
#             self.cache[user_id] = (time.time(), False)
#             return await handler(event, data)
#         except Exception as e:
#             print(f"Ошибка БД: {e}")
#             return await handler(event, data)
#
#         # Обновляем кэш
#         self.cache[user_id] = (time.time(), user.banned)
#
#         if user.banned:
#             await self._send_ban_message(event, data)
#             return
#
#         return await handler(event, data)
#
#     async def _send_ban_message(self, event: types.TelegramObject, data: dict):
#         bot = data["bot"]
#         try:
#             await bot.send_message(
#                 chat_id=event.from_user.id,
#                 text="🚫 Вы забанены и не можете использовать бота"
#             )
#         except Exception as e:
#             print(f"Не удалось отправить сообщение: {e}")