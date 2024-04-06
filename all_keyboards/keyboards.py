from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

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