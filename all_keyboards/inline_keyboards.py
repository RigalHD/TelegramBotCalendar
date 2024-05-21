from aiogram.types import InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from utils.database import BookDatabase


class BookList(CallbackData, prefix="pag"):
    action: str
    book_id: int


def all_books_kb():
    books_dict = BookDatabase.get_amount_of_books(5)
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
    is_description: bool
    book_id: int


def book_info_kb(book_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Описание книги",
        callback_data=BookInfo(
            action="book_description_check",
            is_description=True,
            book_id=book_id).pack()
            )
        )
    builder.row(InlineKeyboardButton(
        text="Дополнительная информация о книге",
        callback_data=BookInfo(
            action="book_additional_info_check",
            is_description=False,
            book_id=book_id).pack()
            )
        )

    builder.row(InlineKeyboardButton(
        text="Назад",
        callback_data=BookInfo(action="return_back", is_description=False, book_id=book_id).pack())
        )
    return builder.as_markup()


def book_info_additions_kb(book_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Назад",
        callback_data=BookInfo(action="return_back_to_info", is_description=False,book_id=book_id).pack())
        )
    return builder.as_markup()
