from config.settings import settings
from db.models import ExchangeSettings, User


def round_amount(amount: int) -> int:
    return (amount // 100) * 100


async def full_calculation(user_id: int, amount: int, currency: str, bot):
    exchange_settings = ExchangeSettings.get()

    if exchange_settings.mode == 'auto':
        USDT_TO_RUB_RATE = 91  # Примерный курс с Bybit
        USDT_TO_THB_RATE = 33.765  # Примерный курс с тайской биржи (с учётом комиссии)
    else:
        USDT_TO_RUB_RATE = exchange_settings.rub_to_usdt
        USDT_TO_THB_RATE = exchange_settings.thb_to_usdt

    # Курсы между валютами
    real_rate = USDT_TO_RUB_RATE / USDT_TO_THB_RATE  # Реальный курс (RUB -> THB)
    client_rate = real_rate * 1.04  # Наценка для клиента
    reverse_rate = real_rate * 0.95  # Обратный курс

    # Перевод в нужные валюты в зависимости от валюты клиента
    user = User.get(user_id=user_id)
    message_text = f"@{user.username} ({user_id}) запрашивает расчет для {amount} {currency}\n\n"

    if currency == "THB":
        thb_to_usdt = amount / USDT_TO_THB_RATE
        thb_to_rub = thb_to_usdt * USDT_TO_RUB_RATE

        thb_to_usdt = round(thb_to_usdt, 2)
        thb_to_rub = round(thb_to_rub, 2)

        client_total = round(amount * client_rate, 2)
        real_total = round(amount * real_rate, 2)
        profit = round(client_total - real_total, 2)

        message_text += (
            f"Курс для клиента (THB): {round(client_rate, 3)} ({round(client_total / amount, 2)} ₽)\n"
            f"Реальный курс: {round(real_rate, 3)} ({round(real_total / amount, 2)} ₽)\n"
            f"Обратный курс: {round(reverse_rate, 3)} ({round(reverse_rate * amount, 2)} ₽)\n\n"
            f"Сумма для клиента: {client_total} ₽\n"
            f"Сумма реальная: {real_total} ₽\n\n"
            f"Зарабатываем с этого: {profit} ₽\n"
        )

    elif currency == "RUB":
        rub_to_usdt = amount * (1 / USDT_TO_RUB_RATE)
        rub_to_thb = rub_to_usdt * USDT_TO_THB_RATE

        rub_to_usdt = round(rub_to_usdt, 2)
        rub_to_thb = round(rub_to_thb, 2)

        client_total = round(amount * client_rate, 2)
        real_total = round(amount * real_rate, 2)
        profit = round(client_total - real_total, 2)

        message_text += (
            f"Курс для клиента (RUB): {round(client_rate, 3)} ({round(client_total / amount, 2)} ₽)\n"
            f"Реальный курс: {round(real_rate, 3)} ({round(real_total / amount, 2)} ₽)\n"
            f"Обратный курс: {round(reverse_rate, 3)} ({round(reverse_rate * amount, 2)} ₽)\n\n"
            f"Сумма для клиента: {client_total} ₽\n"
            f"Сумма реальная: {real_total} ₽\n\n"
            f"Зарабатываем с этого: {profit} ₽\n"
        )

    elif currency == "USDT":
        usdt_to_rub = amount * USDT_TO_RUB_RATE
        usdt_to_thb = amount * USDT_TO_THB_RATE

        usdt_to_rub = round(usdt_to_rub, 2)
        usdt_to_thb = round(usdt_to_thb, 2)

        client_total = round(amount * client_rate, 2)
        real_total = round(amount * real_rate, 2)
        profit = round(client_total - real_total, 2)

        message_text += (
            f"Курс для клиента (USDT): {round(client_rate, 3)} ({round(client_total / amount, 2)} ₽)\n"
            f"Реальный курс: {round(real_rate, 3)} ({round(real_total / amount, 2)} ₽)\n"
            f"Обратный курс: {round(reverse_rate, 3)} ({round(reverse_rate * amount, 2)} ₽)\n\n"
            f"Сумма для клиента: {client_total} ₽\n"
            f"Сумма реальная: {real_total} ₽\n\n"
            f"Зарабатываем с этого: {profit} ₽\n"
        )

    else:
        await bot.send_message(user_id, "Не поддерживаемая валюта для расчета.")
        return

    await bot.send_message(settings.ADMIN_CHAT_ID, message_text)
