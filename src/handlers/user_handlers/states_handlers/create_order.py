# create_order.py (полная версия)
import logging
from datetime import datetime, timedelta

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import (Message, CallbackQuery,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from peewee import DoesNotExist
from config.settings import settings
from db.models import Order, ExchangeSettings, User
from src.app import scheduler
from src.handlers.user_handlers.callbacks_handlers.router import router
from src.schedule import expire_calculation
from src.states.user_states.choose_course import ChooseCourseState
from src.utils import round_amount


@router.message(ChooseCourseState.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        currency = data.get("currency")
        amount = int(message.text)

        order = Order.create(
            user_id=message.from_user.id,
            currency=currency,
            amount=amount,
            chat_id=message.chat.id
        )

        await state.update_data(order_id=order.id)
        rounded_amount = round_amount(amount)

        exchange_settings = ExchangeSettings.get()
        mode = exchange_settings.mode

        if mode == 'auto':
            USDT_TO_RUB = 91.0
            USDT_TO_THB = 33.765
            RUB_TO_USDT = 1 / USDT_TO_RUB
            THB_TO_USDT = 1 / USDT_TO_THB
        else:
            USDT_TO_RUB = exchange_settings.rub_to_usdt
            USDT_TO_THB = exchange_settings.thb_to_usdt
            RUB_TO_USDT = 1 / USDT_TO_RUB
            THB_TO_USDT = 1 / USDT_TO_THB

        response = ""
        if currency == "THB":
            # Расчет для THB
            to_usdt = rounded_amount * THB_TO_USDT
            to_rub = rounded_amount * (THB_TO_USDT * USDT_TO_RUB)

            response = (
                f"{rounded_amount} {currency} - {to_rub:.2f} RUB\n"
                f"Курс: {to_rub / rounded_amount:.4f} RUB/{currency}\n\n"
                f"{rounded_amount} {currency} - {to_usdt:.2f} USDT\n"
                f"Курс: {rounded_amount / to_usdt:.4f} {currency}/USDT"
            )

        elif currency == "RUB":
            # Расчет для RUB
            to_usdt = rounded_amount * RUB_TO_USDT
            to_thb = rounded_amount * (RUB_TO_USDT * USDT_TO_THB)

            response = (
                f"{rounded_amount} {currency} - {to_usdt:.2f} USDT\n"
                f"Курс: {to_usdt / rounded_amount:.4f} USDT/{currency}\n\n"
                f"{rounded_amount} {currency} - {to_thb:.2f} THB\n"
                f"Курс: {rounded_amount / to_thb:.4f} {currency}/THB"
            )

        elif currency == "USDT":
            # Расчет для USDT
            to_rub = rounded_amount * USDT_TO_RUB
            to_thb = rounded_amount * USDT_TO_THB

            response = (
                f"{rounded_amount} {currency} - {to_rub:.2f} RUB\n"
                f"Курс: {to_rub / rounded_amount:.4f} RUB/{currency}\n\n"
                f"{rounded_amount} {currency} - {to_thb:.2f} THB\n"
                f"Курс: {to_thb / rounded_amount:.4f} THB/{currency}"
            )

        else:
            await message.answer("Неподдерживаемая валюта")
            return

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Разместить заказ", callback_data=f"place_order_{order.id}")],
            [InlineKeyboardButton(text="Доставка", callback_data="delivery_info")],
            [InlineKeyboardButton(text="Банкомат", callback_data="atm_info")],
            [InlineKeyboardButton(text="Счёт", callback_data="account_info")],
            [InlineKeyboardButton(text="Ввести новую сумму", callback_data=f"create_order")],
        ])

        msg = await message.answer(response, reply_markup=kb)

        order.message_id = msg.message_id
        order.save()

        scheduler.add_job(
            expire_calculation,
            "date",
            run_date=datetime.now() + timedelta(minutes=10),
            args=[order.id, message.bot],
            id=f"expire_calc_{order.id}",
            jobstore="default"
        )

    except ValueError:
        await message.answer("Введите целое число без пробелов и символов")
    except Exception as e:
        await message.answer("Ошибка обработки запроса")
        logging.error(f"Amount processing error: {str(e)}")


@router.callback_query(F.data.startswith("place_order_"))
async def place_order(callback: CallbackQuery, state: FSMContext):
    try:
        order_id = int(callback.data.split("_")[2])
        order = Order.get_by_id(order_id)
        user = User.get(user_id=order.user_id)
        admin_msg = (
            f"Новый заказ #{order.id}\n"
            f"Сумма: {order.amount} {order.currency}\n"
            f"Клиент: @{user.username} ({user.user_id})"
        )

        admin_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Взять в работу",
                                  callback_data=f"take_order_{order.id}")],
            [InlineKeyboardButton(text='Полный расчёт',
                                  callback_data=f'full_calc_{order.id}')]
        ])

        admin_message = await callback.bot.send_message(
            settings.ADMIN_CHAT_ID,
            admin_msg,
            reply_markup=admin_kb
        )

        order.status = 'pending'
        order.save()

        await callback.message.edit_text("Заказ создан, ожидайте ⏳")

        scheduler.remove_job(f"expire_calc_{order.id}", jobstore="default")

    except DoesNotExist:
        await callback.answer("Заказ не найден!")
    except Exception as e:
        await callback.answer("Ошибка обработки заказа")
        print(f"Order error: {e}")
