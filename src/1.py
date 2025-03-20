from pprint import pprint

import requests

def get_bitkub_price():
    url = 'https://api.bitkub.com/api/market/ticker'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        price_usdt_thb = data

        return price_usdt_thb['THB_USDT']['last']
    else:
        print(f"Ошибка при получении данных: {response.status_code}")
        return None

if __name__ == '__main__':
    price = get_bitkub_price()
    if price:
        pprint(f"Текущий курс USDT/THB: {price} THB")
    else:
        print("Не удалось получить курс.")
