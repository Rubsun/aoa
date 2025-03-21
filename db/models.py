from datetime import datetime

from peewee import *

db = SqliteDatabase('orders.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = IntegerField(primary_key=True, unique=True)
    user_id = IntegerField(null=True)
    username = CharField(null=True)
    chat_id = IntegerField(null=True)
    banned = BooleanField(default=False)


class ExchangeSettings(BaseModel):
    mode = CharField(default="auto")  # Режим: "auto" или "manual"
    thb_to_usdt = FloatField(default=32.6)  # Курс THB/USDT
    rub_to_usdt = FloatField(default=91)  # Курс USDT/RUB
    auto_thb_to_usdt = FloatField(default=32.6)  # Курс THB/USDT
    auto_rub_to_usdt = FloatField(default=91)  # Курс USDT/RUB
    markup_percentage = DecimalField(default=4.0)


class Order(BaseModel):
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('pending', 'Ожидает'),
        ('in_progress', 'В работе'),
        ('expired', 'Просрочен'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен')
    ]

    user_id = IntegerField()
    currency = CharField(max_length=4)
    amount = IntegerField()
    status = CharField(choices=STATUS_CHOICES, default='created')
    created_at = DateTimeField(default=datetime.now)
    message_id = IntegerField(null=True)
    chat_id = IntegerField(null=True)
    operator_id = IntegerField(null=True)


db.connect()
db.create_tables([User, ExchangeSettings, Order], safe=True)
