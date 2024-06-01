from aiogram.utils.keyboard import ReplyKeyboardBuilder
from utils.database import AdminDatabase


# def main_kb(user_id: int) -> ReplyKeyboardBuilder:
#     items = ["Расписание", "Регистрация", "О нас", "Настройки"]
#     AdminDatabase.renew_table()
#     if AdminDatabase.is_admin(user_tg_id=user_id):
#         items.append("/add_book")
#         items.append("/view_random_books")
        
#     builder = ReplyKeyboardBuilder()

#     for item in items:
#         builder.button(text=item)
    
#     return builder.as_markup(
#         resize_keyboard=True,
#         input_field_placeholder="Выберите действие из меню",
#         selective=True,
#         )


def book_age_rating_kb():
    items = ["7-10", "10-14", "14-18"]
    builder = ReplyKeyboardBuilder()
    for item in items:
        builder.button(text=item)
    return builder.as_markup()


