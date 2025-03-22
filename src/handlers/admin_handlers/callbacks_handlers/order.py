from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from peewee import DoesNotExist

from db.models import Order
from src.filters.isAdmin import IsAdmin
from src.handlers.admin_handlers.callbacks_handlers.router import router
from src.utils import full_calculation


@router.callback_query(F.data.startswith("take_order_"), IsAdmin())
async def take_order_handler(callback: CallbackQuery):
    try:
        order_id = int(callback.data.split("_")[2])
        order = Order.get_by_id(order_id)

        order.status = "in_progress"
        order.operator_id = callback.from_user.id
        order.save()

        complete_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Выполнено",
                callback_data=f"complete_order_{order_id}"
            )]
        ])

        await callback.message.edit_text(
            text=f"✅ Заказ #{order_id} взят в работу @{callback.from_user.username}",
            reply_markup=complete_kb
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


@router.callback_query(F.data.startswith("complete_order_"), IsAdmin())
async def complete_order_handler(callback: CallbackQuery):
    try:
        order_id = int(callback.data.split("_")[2])
        order = Order.get_by_id(order_id)

        order.status = "completed"
        order.save()

        await callback.message.edit_text(
            text=f"🏁 Заказ #{order_id} завершен @{callback.from_user.username}",
            reply_markup=None
        )

        await callback.bot.send_message(
            chat_id=order.user_id,
            text=f"Ваш заказ #{order_id} успешно выполнен!"
        )

        await callback.answer("Заказ успешно завершен!")

    except DoesNotExist:
        await callback.answer("Заказ не найден!", show_alert=True)
    except Exception as e:
        await callback.answer("Ошибка при завершении заказа")
        print(f"Complete order error: {e}")


@router.callback_query(F.data.startswith("full_calc_"), IsAdmin())
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
