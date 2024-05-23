from aiogram.types import InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from utils.database import BookDatabase, AdminDatabase


class MainMenu(CallbackData, prefix="pag"):
    action: str


def main_menu_kb(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
        text="Информация",
        callback_data=MainMenu(action="Info_view").pack()
        ),
        width=2
    )
    builder.row(
        InlineKeyboardButton(
        text="Посмотреть книги",
        callback_data=MainMenu(action="Books_view").pack()
        ),
        width=2
    )
    if AdminDatabase.is_admin(user_id):
        builder.row(
            InlineKeyboardButton(
            text="Админ панель",
            callback_data=MainMenu(action="Admin_panel_view").pack()
            ),
            width=2
        )
    return builder.as_markup()


class InfoView(CallbackData, prefix="pag"):
    action: str


def info_view_kb():
    builder = InlineKeyboardBuilder()
    # @router.message(F.text.lower() == "регистрация")
    # async def registration(message: Message):
    #     if message.chat.type == 'private':
    #         await message.answer(f"""Гайд на регистрацию тут
    #                             https://www.youtube.com/watch?v=dQw4w9WgXcQ""")

    # # Все это пока просто плейсхолдеры

    # @router.message(F.text.lower() == "расписание")
    # async def schedule(message: Message):
    #     await message.answer(f"Тихий час по расписанию")


    # @router.message(F.text.lower() == "о нас" )
    # async def about_us(message: Message):
    #     await message.answer(f"Не лезь не в свое дело")
    builder.row(
            InlineKeyboardButton(
            text="О нас",
            callback_data=InfoView(action="About_us").pack()
            ),
            width=5
        )
    builder.row(
        InlineKeyboardButton(
        text="Регистрация",
        callback_data=InfoView(action="Registration").pack()
        ),
        width=5
    )
    builder.row(
        InlineKeyboardButton(
        text="В главное меню",
        callback_data=MainMenu(action="Return_to_main_menu").pack()
    ))
    return builder.as_markup()


class BookList(CallbackData, prefix="pag"):
    action: str
    book_id: int


def all_books_kb():
    books_dict = BookDatabase.get_amount_of_books(5)
    builder = InlineKeyboardBuilder()
    for book_id in books_dict.keys():
        try:
            builder.row(
                InlineKeyboardButton(
                text=books_dict[book_id]["name"],
                callback_data=BookList(action="book_check", book_id=book_id).pack()
                ))
        except KeyError:
            print(books_dict)

    builder.row(
        InlineKeyboardButton(
        text="В главное меню",
        callback_data=MainMenu(action="Return_to_main_menu").pack()
    ))
    
    return builder.as_markup()


class BookInfo(CallbackData, prefix="pag"):
    action: str
    book_id: int


def book_info_kb(book_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Описание книги",
        callback_data=BookInfo(
            action="book_description_check",
            book_id=book_id).pack()
            )
        )
    builder.row(InlineKeyboardButton(
        text="Дополнительная информация о книге",
        callback_data=BookInfo(
            action="book_additional_info_check",
            book_id=book_id).pack()
            )
        )

    builder.row(InlineKeyboardButton(
        text="Назад",
        callback_data=BookInfo(action="return_back", book_id=book_id).pack())
        )
    return builder.as_markup()


def book_info_additions_kb(book_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Назад",
        callback_data=BookInfo(action="return_back_to_book_info", book_id=book_id).pack())
        )
    return builder.as_markup()

