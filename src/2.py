import requests

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
        "payment": BANKDIC.get(bank, []),
        "page": "1",
        "amount": str(summa)
    }

    # Отправка POST-запроса
    try:
        response = requests.post(URL, headers=HEADERS_MAXI, json=DATA)

        if response.status_code != 200:
            return 0

        pretty_json = response.json()

        # Проверяем на успешность и наличие данных
        if pretty_json.get("ret_code") != 0 or not pretty_json.get("result", {}).get("items"):
            return 0

        # Извлечение цен
        list_json = [float(i['price']) for i in pretty_json['result']['items']]

        # Обрезка первых двух элементов, если они есть
        if len(list_json) > 2:
            list_json = list_json[2:]

        if not list_json:
            return 0

        # Дополнительное условие
        if tradeType == "BUY" and fiat == "THB":
            return 0

        # Возвращаем среднее значение
        average_price = sum(list_json) / len(list_json)
        return average_price

    except Exception as e:
        print(f"Ошибка при обработке: {e}")
        return 0

# Пример вызова
result = bybit_check(1000, "СберБанк", "BUY", "USDT", "RUB")
print("Средняя цена:", result)
