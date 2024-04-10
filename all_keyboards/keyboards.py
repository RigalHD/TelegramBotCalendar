from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Расписание"),
        ],
        [
            KeyboardButton(text="Регистрация"),
        ],
        [    
            KeyboardButton(text="О нас"),
        ],
        [
            KeyboardButton(text="Настройки"),
        ]
    ], 
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите действие из меню",
    selective=True,
)


def book_age_rating():
    items = ["7-10", "10-14", "14-18"]
    builder = ReplyKeyboardBuilder()
    for item in items:
        builder.button(text=item)
    return builder.as_markup()


