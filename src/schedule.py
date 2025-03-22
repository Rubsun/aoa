import requests
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.settings import settings
from db.models import Order, ExchangeSettings

scheduler = AsyncIOScheduler()


async def expire_order(user_id: int, message_id: int, bot):
    await bot.send_message(user_id, "Время истекло! Нужно пересчитать сумму.")
    await bot.edit_message_text(text="Заказ просрочен", chat_id=settings.ADMIN_CHAT_ID, message_id=message_id)


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


    except Order.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error in expire_calculation: {e}")



def get_bitkub_price():
    url = 'https://api.bitkub.com/api/market/ticker'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        thb_usdt_data = data.get('THB_USDT', {})
        if thb_usdt_data:
            highest_bid = thb_usdt_data.get('highestBid')
            lowest_ask = thb_usdt_data.get('lowestAsk')

            if highest_bid is not None and lowest_ask is not None:
                average_rate = (highest_bid + lowest_ask) / 2
                return average_rate
            else:
                print("Ошибка: не удалось найти значения highestBid или lowestAsk.")
                return None
        else:
            print("Ошибка: данные для THB_USDT не найдены.")
            return None
    else:
        print(f"Ошибка при получении данных: {response.status_code}")
        return None


def bybit_check(summa: float, bank: str, tradeType: str, asset: str, fiat: str = 'RUB'):
    URL = "https://api2.bybit.com/fiat/otc/item/online"

    if bank == "АльфаБанк":
        return 0

    TRADETYPEDIC = {
        "BUY": "1",  # Покупка
        "SELL": "0"  # Продажа
    }

    BANKDIC = {
        "СберБанк": ["582"],
        "Тинькофф": ["581"],
        "Райффайзен": ["643"]
    }

    HEADERS_MAXI = {
        "Host": "api2.bybit.com",
        "Origin": "https://www.bybit.com"
    }

    DATA = {
        "tokenId": asset,
        "currencyId": fiat,
        "authMaker": False,
        "side": TRADETYPEDIC.get(tradeType, "1"),
        # "payment": BANKDIC.get(bank, []),
        "page": "1",
        "amount": str(summa)
    }

    try:
        response = requests.post(URL, headers=HEADERS_MAXI, json=DATA)

        if response.status_code != 200:
            return 0

        pretty_json = response.json()

        if pretty_json.get("ret_code") != 0 or not pretty_json.get("result", {}).get("items"):
            return 0

        list_json = [float(i['price']) for i in pretty_json['result']['items']]

        if len(list_json) > 2:
            list_json = list_json[2:]

        if not list_json:
            return 0

        if tradeType == "BUY" and fiat == "THB":
            return 0

        average_price = sum(list_json) / len(list_json)
        return average_price

    except Exception as e:
        print(f"Ошибка при обработке: {e}")
        return 0


def update_exchange_rates():
    """Основная функция для обновления курсов"""
    try:
        # Получаем курс THB/USDT от Bitkub
        thb_rate = get_bitkub_price()
        if thb_rate and thb_rate > 0:
            ExchangeSettings.update(auto_thb_to_usdt=thb_rate).execute()
            print(f"Обновлен курс THB/USDT: {thb_rate}")

        rub_rate = bybit_check(
            summa=10000,
            bank="СберБанк",
            tradeType="BUY",
            asset="USDT",
            fiat="RUB"
        )
        if rub_rate and rub_rate > 0:
            ExchangeSettings.update(auto_rub_to_usdt=rub_rate).execute()
            print(f"Обновлен курс RUB/USDT: {rub_rate}")

    except Exception as e:
        print(f"Ошибка при обновлении курсов: {str(e)}")

