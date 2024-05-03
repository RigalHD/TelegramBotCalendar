from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
import sqlite3


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
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        books_dict = {}
        all_books = cursor.execute("SELECT * FROM books").fetchall()
        books_keys = [column[1] for column in cursor.execute(
                "PRAGMA table_info(books)").fetchall()]
        for book in all_books:
            books_dict[book[0]] = {}
            for key, value in zip(books_keys[1:], book[1:]):
                books_dict[book[0]][key] = value

    builder = InlineKeyboardBuilder()
    for book_id in books_dict.keys():
        builder.row(InlineKeyboardButton(
            text=books_dict[book_id]["name"],
            callback_data=BookList(action="book_check", book_id=book_id).pack())
            ) 
    return builder.as_markup()


class BookInfo(CallbackData, prefix="pag"):
    action: str
    choice: str
    column_name: str
    book_id: int


def book_info_kb(book_info: dict, book_id: int):
    builder = InlineKeyboardBuilder()
    for key, value in book_info.items():
        builder.row(InlineKeyboardButton(
            text=key,
            callback_data=BookInfo(action="book_info_check", choice=key, column_name=value, book_id=book_id).pack())
            )
        print(key)
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
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        books_columns = [
            column[1] for column in cursor.execute(
                "PRAGMA table_info(books)"
                ).fetchall()
            ]
        book_info = zip(
            books_columns,
            cursor.execute("""SELECT * FROM books WHERE book_id = ?""", (book_id,)).fetchone()
            )
    builder.row(InlineKeyboardButton(
        text=book_info["name"],
        callback_data=BookList(action="book_check", book_id=book_id).pack())
        ) 
    return builder.as_markup()
