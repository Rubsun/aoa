from aiogram import F
from aiogram.types import CallbackQuery
from peewee import DoesNotExist

from db.models import Order
from src.handlers.admin_handlers.callbacks_handlers.router import router
from src.utils import full_calculation


@router.callback_query(F.data.startswith("take_order_"))
async def take_order_handler(callback: CallbackQuery):
    try:
        order_id = int(callback.data.split("_")[2])
        order = Order.get_by_id(order_id)

        order.status = "in_progress"
        order.operator_id = callback.from_user.id
        order.save()

        await callback.message.edit_text(
            text=f"✅ Заказ #{order_id} взят в работу @{callback.from_user.username}",
            reply_markup=None
        )

        await callback.bot.send_message(
            chat_id=order.user_id,
            text=f"Ваш заказ #{order_id} принят в работу!\n"
                 f"Оператор: @{callback.from_user.username}"
        )

    except DoesNotExist:
        await callback.answer("Заказ не найден!", show_alert=True)
    except Exception as e:
        await callback.answer("Ошибка при обработке заказа")
        print(f"Take order error: {e}")


@router.callback_query(F.data.startswith("full_calc_"))
async def full_calculation_handler(callback: CallbackQuery):
    try:
        order_id = int(callback.data.split("_")[2])
        await full_calculation(order_id, callback.bot)
        await callback.answer("Расчёт отправлен в чат")
    except DoesNotExist:
        await callback.answer("Заказ не найден!", show_alert=True)
    except Exception as e:
        await callback.answer("Ошибка при расчете")
        print(f"Full calculation error: {e}")
