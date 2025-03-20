from datetime import datetime, timedelta

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config.settings import settings
from db.models import ExchangeSettings
from src.app import scheduler
from src.handlers.user_handlers.callbacks_handlers.router import router
from src.schedule import expire_calculation
from src.states.user_states.choose_course import ChooseCourseState
from src.utils import round_amount


@router.message(ChooseCourseState.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        await state.update_data(amount=amount)
        rounded_amount = round_amount(amount)

        data = await state.get_data()
        currency = data.get("currency")

        exchange_settings = ExchangeSettings.get()
        mode = exchange_settings.mode
        if mode == 'auto':
            USDT_TO_RUB_RATE = 91  # Примерный курс с Bybit
            USDT_TO_THB_RATE = 33.765  # Примерный курс с тайской биржи (с учётом комиссии)
        else:
            USDT_TO_RUB_RATE = exchange_settings.rub_to_usdt
            USDT_TO_THB_RATE = exchange_settings.thb_to_usdt

        RUB_TO_USDT_RATE = 1 / USDT_TO_RUB_RATE  # RUB -> USDT
        THB_TO_RUB_RATE = USDT_TO_RUB_RATE / USDT_TO_THB_RATE  # THB -> RUB
        RUB_TO_THB_RATE = USDT_TO_THB_RATE / USDT_TO_RUB_RATE  # RUB -> THB

        response_message = ""

        if currency == "THB":
            thb_to_usdt = rounded_amount / USDT_TO_THB_RATE
            thb_to_rub = rounded_amount * THB_TO_RUB_RATE

            thb_to_usdt = round(thb_to_usdt, 2)
            thb_to_rub = round(thb_to_rub, 2)

            response_message = (
                f"{rounded_amount} THB ≈ {thb_to_rub} RUB\n"
                f"Курс: {round(thb_to_rub / rounded_amount, 3)} RUB/THB\n\n"
                f"{rounded_amount} THB ≈ {thb_to_usdt} USDT\n"
                f"Курс: {round(rounded_amount / thb_to_usdt, 3)} THB/USDT"
            )

        elif currency == "RUB":
            rub_to_usdt = rounded_amount * RUB_TO_USDT_RATE
            rub_to_thb = rounded_amount * RUB_TO_THB_RATE

            rub_to_usdt = round(rub_to_usdt, 2)
            rub_to_thb = round(rub_to_thb, 2)

            response_message = (
                f"{rounded_amount} RUB ≈ {rub_to_usdt} USDT\n"
                f"Курс: {round(rounded_amount / rub_to_usdt, 3)} RUB/USDT\n\n"
                f"{rounded_amount} RUB ≈ {rub_to_thb} THB\n"
                f"Курс: {round(rounded_amount / rub_to_thb, 3)} RUB/THB"
            )

        elif currency == "USDT":
            usdt_to_rub = rounded_amount * USDT_TO_RUB_RATE
            usdt_to_thb = rounded_amount * USDT_TO_THB_RATE

            usdt_to_rub = round(usdt_to_rub, 2)
            usdt_to_thb = round(usdt_to_thb, 2)

            response_message = (
                f"{rounded_amount} USDT ≈ {usdt_to_rub} RUB\n"
                f"Курс: {round(rounded_amount / usdt_to_rub, 3)} USDT/RUB\n\n"
                f"{rounded_amount} USDT ≈ {usdt_to_thb} THB\n"
                f"Курс: {round(rounded_amount / usdt_to_thb, 3)} USDT/THB"
            )

        else:
            await message.answer("Доступны только расчеты из RUB, THB и USDT.")
            return

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Разместить заказ", callback_data="place_order")],
            [InlineKeyboardButton(text="Доставка", callback_data="delivery")],
            [InlineKeyboardButton(text="Банкомат", callback_data="atm")],
            [InlineKeyboardButton(text="Счёт", callback_data="account")],
            [InlineKeyboardButton(text="Ввести новую сумму", callback_data=f"choose_{currency}")],
        ])

        msg = await message.answer(response_message, reply_markup=kb)

        scheduler.add_job(
            expire_calculation,
            "date",
            run_date=datetime.now() + timedelta(seconds=15),
            args=[message.chat.id, msg.message_id, message.bot],
            id=f"expire_calc_{msg.message_id}",
            jobstore="default"
        )
    except ValueError:
        await message.answer("Введите корректное число.")


@router.callback_query(F.data == "place_order")
async def place_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    currency = data.get("currency")
    amount = data.get("amount")
    user_id = callback.from_user.id
    if not amount:
        await callback.message.answer("Произошла ошибка. Попробуйте заново.")
        return

    order_message = (
        f"Новый заказ!\n"
        f"Сумма: {amount} {currency}\n"
        f"Клиент: @{callback.from_user.username or callback.from_user.id}"
    )

    operator_msg = await callback.bot.send_message(settings.ADMIN_CHAT_ID, order_message)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Взять в работу", callback_data=f"take_order_{operator_msg.message_id}_{user_id}")],
        [InlineKeyboardButton(text='Полный расчёт',
                              callback_data=f'f_c_{operator_msg.message_id}_{user_id}_{amount}_{currency}')],

    ])
    await callback.bot.edit_message_reply_markup(chat_id=settings.ADMIN_CHAT_ID, message_id=operator_msg.message_id,
                                                 reply_markup=kb)

    await callback.message.edit_text(text="Заказ создан, ожидайте ⏳")
    scheduler.remove_job(f"expire_calc_{callback.message.message_id}", jobstore="default")

    # scheduler.add_job(
    #     expire_order,
    #     "date",
    #     run_date=datetime.now() + timedelta(minutes=10),
    #     args=[callback.from_user.id, operator_msg.message_id, callback.bot],
    #     id=f"expire_order_{operator_msg.message_id}"
    # )

    # await state.clear()
