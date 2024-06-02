from aiogram.utils.keyboard import ReplyKeyboardBuilder


def book_age_rating_kb():
    items = ["7-10", "10-14", "14-18"]
    builder = ReplyKeyboardBuilder()
    for item in items:
        builder.button(text=item)
    return builder.as_markup()
