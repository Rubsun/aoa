from decimal import Decimal, ROUND_HALF_UP

from config.settings import settings
from db.models import Order, ExchangeSettings, User


def round_amount(amount: int) -> int:
    return (amount // 100) * 100


def round_value(value, precision=2):
    return value.quantize(Decimal('1.' + '0' * precision), rounding=ROUND_HALF_UP)


async def full_calculation(order_id: int, bot):
    try:
        # Получаем данные заказа и пользователя
        order = Order.get_by_id(order_id)
        user = User.get(User.user_id == order.user_id)

        # Получаем актуальные настройки обмена
        exchange_settings = ExchangeSettings.get()

        # Определяем базовые курсы
        if exchange_settings.mode == 'auto':
            base_rates = {
                'USDT/RUB': Decimal(str(exchange_settings.auto_rub_to_usdt)),
                'USDT/THB': Decimal(str(exchange_settings.auto_thb_to_usdt)),
            }
        else:
            base_rates = {
                'USDT/RUB': Decimal(str(exchange_settings.rub_to_usdt)),
                'USDT/THB': Decimal(str(exchange_settings.thb_to_usdt)),
            }

        base_rates['RUB/THB'] = base_rates['USDT/THB'] / base_rates['USDT/RUB']
        base_rates['THB/RUB'] = Decimal(1) / base_rates['RUB/THB']
        base_rates['RUB/USDT'] = Decimal(1) / base_rates['USDT/RUB']
        base_rates['THB/USDT'] = Decimal(1) / base_rates['USDT/THB']

        # Наценки и коэффициенты
        markup = Decimal(1 + exchange_settings.markup_percentage / 100)
        discount = Decimal('0.95')

        # Основные параметры
        amount = Decimal(str(order.amount))
        currency = order.currency

        conversion_results = {}
        if currency == 'RUB':
            conversion_results['USDT'] = amount * base_rates['RUB/USDT']
            conversion_results['THB'] = amount * base_rates['RUB/THB']
            client_total = amount * markup
        elif currency == 'THB':
            conversion_results['USDT'] = amount * base_rates['THB/USDT']
            conversion_results['RUB'] = amount * base_rates['THB/RUB']
            client_total = conversion_results['RUB'] * markup
        elif currency == 'USDT':
            conversion_results['RUB'] = amount * base_rates['USDT/RUB']
            conversion_results['THB'] = amount * base_rates['USDT/THB']
            client_total = conversion_results['RUB'] * markup
        else:
            raise ValueError(f"Неподдерживаемая валюта: {currency}")

        real_total = conversion_results.get('RUB', amount)
        profit = client_total - real_total
        estimated_profit = profit * discount

        message_text = (
                f"📊 <b>Полный расчет заказа #{order_id}</b>\n"
                f"👤 Клиент: {user.username} ({user.user_id})\n"
                f"💱 Валюта: {currency}\n"
                f"💵 Сумма: {amount} {currency}\n"
                f"📅 Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                f"💸 <b>Финансовые показатели:</b>\n\n"
                f"Для клиента: {round_value(client_total)} RUB\n"
                f"Реальная стоимость: {round_value(real_total)} RUB\n"
                f"Прибыль: +{round_value(profit)} RUB\n"
                f"Примерная прибыль: +{round_value(estimated_profit)} RUB\n\n"
                f"📈 <b>Курсы обмена:</b>\n"
                f"Клиентский: {round_value(base_rates['USDT/RUB'] * markup, 3)} RUB/USDT\n"
                f"Рыночный: {round_value(base_rates['USDT/RUB'] / base_rates['USDT/THB'], 3)} RUB/THB\n"
                f"Обратный: {round_value(base_rates['USDT/RUB'] * discount / base_rates['USDT/THB'], 3)} RUB/THB\n\n"
                f"🔀 <b>Конверсии:</b>\n"
                + "\n".join([f"• {amount} {currency} → {round_value(v)} {k}" for k, v in conversion_results.items()])
        )

        await bot.send_message(chat_id=settings.ADMIN_CHAT_ID, text=message_text, parse_mode="HTML")
    except Order.DoesNotExist:
        await bot.send_message(settings.ADMIN_CHAT_ID, f"❌ Заказ #{order_id} не найден!")
    except User.DoesNotExist:
        await bot.send_message(settings.ADMIN_CHAT_ID, f"❌ Пользователь для заказа #{order_id} не найден!")
    except Exception as e:
        await bot.send_message(settings.ADMIN_CHAT_ID, f"⚠️ Ошибка расчета: {str(e)}")
        raise
