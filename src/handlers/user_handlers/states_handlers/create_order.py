import logging
from datetime import datetime, timedelta
from decimal import Decimal

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import (Message, CallbackQuery,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from peewee import DoesNotExist

from config.settings import settings
from db.models import Order, ExchangeSettings, User
from src.app import scheduler
from src.handlers.user_handlers.callbacks_handlers.router import router
from src.handlers.user_handlers.commands_handlers.start import cmd_start
from src.schedule import expire_calculation
from src.states.user_states.choose_course import ChooseCourseState
from src.utils import round_amount


@router.message(ChooseCourseState.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        currency = data.get("currency")
        amount = int(message.text)
        rounded_amount = round_amount(amount)

        order = Order.create(
            user_id=message.from_user.id,
            currency=currency,
            amount=rounded_amount,
            chat_id=message.chat.id
        )

        await state.update_data(order_id=order.id)
        rounded_amount = round_amount(amount)

        exchange_settings = ExchangeSettings.get()
        mode = exchange_settings.mode

        markup_percentage = exchange_settings.markup_percentage  # Get markup percentage from DB
        markup_factor = 1 + (markup_percentage / 100)

        if mode == 'auto':
            USDT_TO_RUB = Decimal(str(exchange_settings.auto_rub_to_usdt)) * markup_factor
            USDT_TO_THB = Decimal(str(exchange_settings.auto_thb_to_usdt)) * markup_factor
        else:
            USDT_TO_RUB = exchange_settings.rub_to_usdt * markup_factor
            USDT_TO_THB = exchange_settings.thb_to_usdt * markup_factor

        RUB_TO_USDT = 1 / USDT_TO_RUB
        THB_TO_USDT = 1 / USDT_TO_THB

        response = ""
        if currency == "THB":
            to_usdt = rounded_amount * THB_TO_USDT
            to_rub = rounded_amount * (THB_TO_USDT * USDT_TO_RUB)

            response = (
                f"{rounded_amount} {currency} - {int(to_rub)} RUB\n"
                f"Курс: {to_rub / rounded_amount:.3f} RUB/{currency}\n\n"
                f"{rounded_amount} {currency} - {to_usdt:.3f} USDT\n"
                f"Курс: {rounded_amount / to_usdt:.3f} {currency}/USDT"
            )

        elif currency == "RUB":
            to_usdt = rounded_amount * RUB_TO_USDT
            to_thb = rounded_amount * (RUB_TO_USDT * USDT_TO_THB)

            response = (
                f"{int(rounded_amount)} {currency} - {to_usdt:.3f} USDT\n"
                f"Курс: {to_usdt / rounded_amount:.3f} USDT/{currency}\n\n"
                f"{int(rounded_amount)} {currency} - {to_thb:.3f} THB\n"
                f"Курс: {rounded_amount / to_thb:.3f} {currency}/THB"
            )

        elif currency == "USDT":
            to_rub = rounded_amount * USDT_TO_RUB
            to_thb = rounded_amount * USDT_TO_THB

            response = (
                f"{rounded_amount} {currency} - {int(to_rub)} RUB\n"
                f"Курс: {to_rub / rounded_amount:.3f} RUB/{currency}\n\n"
                f"{rounded_amount} {currency} - {to_thb:.3f} THB\n"
                f"Курс: {to_thb / rounded_amount:.3f} THB/{currency}"
            )

        else:
            await message.answer("Неподдерживаемая валюта")
            return

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Разместить заказ", callback_data=f"confirm_order_{order.id}")],
            [InlineKeyboardButton(text="Доставка", callback_data="delivery_info")],
            [InlineKeyboardButton(text="Банкомат", callback_data="atm_info")],
            [InlineKeyboardButton(text="Счёт", callback_data="account_info")],
            [InlineKeyboardButton(text="Ввести новую сумму", callback_data=f"create_order")],
        ])

        msg = await message.answer(response, reply_markup=kb)

        order.message_id = msg.message_id
        order.save()

        # Отправка информации в админский чат
        user = User.get(user_id=message.from_user.id)
        admin_msg = (
            f"Запрос курса от @{user.username} ({user.user_id})\n"
            f"Сумма: {rounded_amount} {currency}"
        )
        await message.bot.send_message(settings.ADMIN_CHAT_ID, admin_msg)

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
            [InlineKeyboardButton(text="Взять в работу", callback_data=f"take_order_{order.id}")],
            [InlineKeyboardButton(text='Полный расчёт', callback_data=f'full_calc_{order.id}')],
            [InlineKeyboardButton(text='Проверить пользователя',
                                  url=f'https://t.me/lolsbotcatcherbot?start={user.user_id}')]
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


@router.callback_query(F.data.startswith("confirm_order_"))
async def confirm_order(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data=f"place_order_{order_id}")],
        [InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_order_{order_id}")],
    ])
    await callback.message.edit_text("Вы уверены, что хотите разместить заказ?", reply_markup=kb)


@router.callback_query(F.data.startswith("cancel_order_"))
async def cancel_order(callback: CallbackQuery):
    order_id = callback.data.split("_")[2]
    order = Order.get_by_id(order_id)
    order.status = 'canceled'
    order.save()
    await callback.message.edit_text("Ваш заказ отменен.")
    await cmd_start(callback.message)
