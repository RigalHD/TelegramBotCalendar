from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from utils.database import BookDatabase


def main_kb(user_id: int) -> ReplyKeyboardBuilder:
    items = ["Расписание", "Регистрация", "О нас", "Настройки"]
    admins = [997987348]
    if user_id in admins:
        items.append("/add_book")
        items.append("/view_random_books")
    builder = ReplyKeyboardBuilder()
    for item in items:
        builder.button(text=item)
    
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите действие из меню",
        selective=True,
        )


def book_age_rating_kb():
    items = ["7-10", "10-14", "14-18"]
    builder = ReplyKeyboardBuilder()
    for item in items:
        builder.button(text=item)
    return builder.as_markup()


