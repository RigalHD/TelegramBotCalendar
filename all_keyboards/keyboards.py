from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.types.input_media_photo import InputMediaPhoto
import sqlite3

from utils.database import BookDatabase

def main_kb(user_id: int) -> ReplyKeyboardBuilder:
    items = ["Расписание", "Регистрация", "О нас", "Настройки"]
    admins = [997987348]
    if user_id in admins:
        items.append("/add_book")
        items.append("/test_kb")
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


class BookList(CallbackData, prefix="pag"):
    action: str
    book_id: int


def all_books_kb():
    books_dict = BookDatabase.get_all_books()
    builder = InlineKeyboardBuilder()
    for book_id in books_dict.keys():
        try:
            builder.row(InlineKeyboardButton(
                text=books_dict[book_id]["name"],
                callback_data=BookList(action="book_check", book_id=book_id).pack())
                )
        except KeyError:
            print(books_dict)
    return builder.as_markup()


class BookInfo(CallbackData, prefix="pag"):
    action: str
    choice: str
    column_name: str
    book_id: int


def book_info_kb(book_id: int):
    builder = InlineKeyboardBuilder()
    book = BookDatabase(book_id)
    for key, value in book.get_columns_names_dict().items():
        try:
            builder.row(InlineKeyboardButton(
                text=key,
                callback_data=BookInfo(action="book_info_check", choice=str(key), column_name=str(value), book_id=book_id).pack())
                )
            # print(key, value, book_id, sep="\n")
        except ValueError:
            # print("====")
            # print(key, value, book_id, sep="\n")
            return
    builder.row(InlineKeyboardButton(
        text="Назад",
        callback_data=BookInfo(action="return_back", choice="-", column_name="-", book_id=book_id).pack())
        )
    return builder.as_markup()


def book_info_additions_kb(book_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Назад",
        callback_data=BookInfo(action="return_back_to_info", choice="-", column_name="-", book_id=book_id).pack())
        )
    return builder.as_markup()
