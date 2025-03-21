from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.settings import settings
from db.models import Order

scheduler = AsyncIOScheduler()


async def expire_order(user_id: int, message_id: int, bot):
    await bot.send_message(user_id, "Время истекло! Нужно пересчитать сумму.")
    await bot.edit_message_text(text="Заказ просрочен", chat_id=settings.ADMIN_CHAT_ID, message_id=message_id)


#
# async def expire_calculation(user_id: int, message_id: int, bot):
#     await bot.edit_message_text(
#         chat_id=user_id,
#         message_id=message_id,
#         text="⏳ Время истекло! Курс мог измениться. Сделайте новый расчет.",
#         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text="🔄 Сделать новый расчет", callback_data="create_order")]
#         ])
#     )

async def expire_calculation(order_id: int, bot):
    try:
        order = Order.get_by_id(order_id)

        if order.status == 'created':
            await bot.edit_message_text(
                chat_id=order.user_id,
                message_id=order.message_id,
                text="⏳ Время истекло! Курс мог измениться. Сделайте новый расчет.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="🔄 Сделать новый расчет",
                        callback_data="create_order"
                    )]
                ])
            )

            order.status = 'expired'
            order.save()

            # scheduler.remove_job(f"expire_calc_{order_id}")

    except Order.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error in expire_calculation: {e}")
