from aiogram.types import CallbackQuery, FSInputFile
from aiogram import Router, F
import sqlite3

from all_keyboards import keyboards


router = Router()


@router.callback_query(keyboards.BookList.filter(F.action == "book_check"))
async def booklist_handler(query: CallbackQuery, callback_data: keyboards.BookList):
    book_id = int(callback_data.book_id)

    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        book_info = cursor.execute("""
                                   SELECT *
                                   FROM books WHERE id = ?
                                   """,
                                   (book_id,)
                                   ).fetchone()
        photo_path = book_info[-1]
        books_columns = [column[1] for column in cursor.execute(
        "PRAGMA table_info(books)").fetchall()]

        book_info = dict(zip(
            ("Название", "Описание", "Автор", "Жанр", "Год", "Издательство", "Рейтинг", "Возраcт"),
            books_columns[1:-1]
        ))

        await query.message.answer_photo(
            photo=FSInputFile(photo_path),
            caption="Узнай о книге больше",
            reply_markup=keyboards.book_info_kb(book_info, book_id)
            )

        # book_info_message: str = "\n".join([f"{key}: {value} \n{'-' * 20}" for key, value in book_info.items()])
        
        # await query.message.answer_photo(photo=FSInputFile(photo_path))
        # await query.message.answer(text=book_info_message)


@router.callback_query(keyboards.BookInfo.filter(F.action == "book_info_check"))
async def bookinfo_handler(query: CallbackQuery, callback_data: keyboards.BookList):
    print(callback_data.column_name)


@router.callback_query(keyboards.BookInfo.filter(F.action == "return_back"))
async def bookinfo_back_handler(query: CallbackQuery, callback_data: keyboards.BookList):
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        books_columns = [column[1] for column in cursor.execute(
        "PRAGMA table_info(books)").fetchall()]

        book_info = dict(zip(
            ("Название", "Описание", "Автор", "Жанр", "Год", "Издательство", "Рейтинг", "Возраcт"),
            books_columns[1:-1]
        ))
        photo_path = cursor.execute("""
                                    SELECT image
                                    FROM books WHERE id = ?
                                    """,
                                    (callback_data.book_id,)
                                    ).fetchone()
        await query.message.edit_media(
            photo=FSInputFile(*photo_path),
            caption="Узнай о книге больше",
            reply_markup=keyboards.book_info_kb(book_info, book_id=callback_data.book_id)
        )