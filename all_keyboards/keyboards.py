from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_kb(user_id: int) -> ReplyKeyboardBuilder:
    items = ["Расписание", "Регистрация", "О нас", "Настройки"]
    admins = [997987348]
    if user_id in admins:
        items.append("/add_book")
    builder = ReplyKeyboardBuilder()
    for item in items:
        builder.button(text=item)
    
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите действие из меню",
        selective=True,
        )


def book_age_rating():
    items = ["7-10", "10-14", "14-18"]
    builder = ReplyKeyboardBuilder()
    for item in items:
        builder.button(text=item)
    return builder.as_markup()


