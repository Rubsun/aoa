from pprint import pprint

import requests


def get_bitkub_price():
    url = 'https://api.bitkub.com/api/market/ticker'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Получаем курс USDT/THB
        thb_usdt_data = data.get('THB_USDT', {})
        if thb_usdt_data:
            highest_bid = thb_usdt_data.get('highestBid')
            lowest_ask = thb_usdt_data.get('lowestAsk')

            if highest_bid is not None and lowest_ask is not None:
                # Рассчитываем средний курс
                average_rate = (highest_bid + lowest_ask) / 2
                print(f"Средний курс USDT/THB: {average_rate:.2f} THB")
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

def get_bitkub_avg_price():
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
    price = get_bitkub_avg_price()
    if price:
        pprint(f"Текущий курс USDT/THB: {price} THB")
    else:
        print("Не удалось получить курс.")

    get_bitkub_price()