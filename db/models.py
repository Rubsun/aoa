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


#
# class Order(BaseModel):
#     id = IntegerField(primary_key=True, unique=True)
#     user = ForeignKeyField(User, backref='orders')  # Связь с пользователем
#     order_status = CharField(default='new')  # Статус заказа (new, in_progress, completed, expired)
#     created_at = DateTimeField(default=datetime.now)  # Дата и время создания заказа
#     updated_at = DateTimeField(default=datetime.now)  # Дата и время последнего обновления заказа
#     amount = DecimalField(null=True)  #

class ExchangeSettings(BaseModel):
    mode = CharField(default="auto")  # Режим: "auto" или "manual"
    rub_to_thb = FloatField(default=2.826)  # Курс RUB/THB
    thb_to_usdt = FloatField(default=32.6)  # Курс THB/USDT
    rub_to_usdt = FloatField(default=0.013)  # Курс USDT/RUB


# def add_order(user_id, amount):
#     user = User.get(User.user_id == user_id)  # Получаем пользователя по user_id
#     order = Order.create(user=user, amount=amount, order_status='new')
#     return order
#
# def get_order_by_id(order_id):
#     order = Order.get(Order.id == order_id)
#     if order is None:
#         return None
#     return order
#
# def update_order_status(order_id, status):
#     order = Order.get(Order.id == order_id)
#     if order is None:
#         return None
#     order.order_status = status
#     order.updated_at = datetime.now()  # Обновляем время
#     order.save()
#     return order
#
# def get_orders_by_user(user_id):
#     user = User.get(User.user_id == user_id)
#     if user is None:
#         return []
#     orders = user.orders  # Получаем все заказы пользователя
#     return orders


db.connect()
db.create_tables([User, ExchangeSettings], safe=True)
