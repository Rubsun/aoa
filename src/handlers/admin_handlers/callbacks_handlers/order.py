from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config.settings import settings
from src.handlers.admin_handlers.callbacks_handlers.router import router
from src.utils import full_calculation


@router.callback_query(F.data.startswith("take_order_"))
async def take_order(callback: CallbackQuery, state: FSMContext):
    _, _, message_id, user_id = callback.data.split("_")
    data = await state.get_data()
    amount = data.get("amount")
    print(amount)
    # scheduler.remove_job(f"expire_order_{message_id}")
    username = callback.from_user.username

    await callback.bot.send_message(user_id, f"Ваша заявка принята в работу. С вами свяжется @{username}.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выполнена", callback_data=f"complete_order_{message_id}_{user_id}")],
    ])
    await callback.bot.edit_message_reply_markup(chat_id=settings.ADMIN_CHAT_ID, message_id=int(message_id),
                                                 reply_markup=kb)


@router.callback_query(F.data.startswith("complete_order_"))
async def complete_order(callback: CallbackQuery):
    _, _, message_id, user_id = callback.data.split("_")

    username = callback.from_user.username

    await callback.bot.send_message(user_id, "Ваша заявка выполнена!")

    await callback.bot.edit_message_text(text=f"Заявка выполнена @{username}", chat_id=settings.ADMIN_CHAT_ID,
                                         message_id=int(message_id))


@router.callback_query(F.data.startswith("f_c_"))
async def handle_full_calculation(callback: CallbackQuery, state: FSMContext):
    _, _, message_id, user_id, amount, currancy = callback.data.split("_")

    if not amount:
        await callback.message.answer("Произошла ошибка. Попробуйте заново.")
        return

    await full_calculation(callback.from_user.id, int(amount), currancy, callback.bot)
    # await callback.answer("Полный расчет отправлен операторам.")
