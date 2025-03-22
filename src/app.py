import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.triggers.interval import IntervalTrigger

from config.settings import settings
from db.models import ExchangeSettings
from src.bot import setup_bot, setup_dp
from src.handlers.admin_handlers.callbacks_handlers.router import router as admin_callbacks_router
from src.handlers.admin_handlers.commands_handlers.router import router as admin_commands_router
from src.handlers.admin_handlers.state_handlers.router import router as admin_state_router
from src.handlers.user_handlers.callbacks_handlers.router import router as user_callbacks_router
from src.handlers.user_handlers.commands_handlers.router import router as user_commands_router
from src.handlers.user_handlers.states_handlers.router import router as user_states_router
from src.middlewares.ban_middleware import BanMiddleware
from src.schedule import scheduler, update_exchange_rates


async def start_polling():
    if not ExchangeSettings.select().exists():
        ExchangeSettings.create()

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(BanMiddleware())

    setup_dp(dp)
    setup_bot(bot)

    dp.include_router(user_commands_router)
    dp.include_router(admin_commands_router)
    dp.include_router(admin_state_router)
    dp.include_router(user_callbacks_router)
    dp.include_router(user_states_router)
    dp.include_router(admin_callbacks_router)

    scheduler.add_job(
        update_exchange_rates,
        trigger=IntervalTrigger(minutes=10),
        id='exchange_rate_update',
        replace_existing=True
    )

    scheduler.start()

    await bot.delete_webhook()

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_polling())
