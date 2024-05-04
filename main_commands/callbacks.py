from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import CallbackQuery, FSInputFile
from aiogram import Router, F

from utils.database import BookDatabase
from config import all_books_image_path
from all_keyboards import keyboards


router = Router()


@router.callback_query(keyboards.BookList.filter(F.action == "book_check"))
async def booklist_handler(query: CallbackQuery, callback_data: keyboards.BookList):
    book = BookDatabase(int(callback_data.book_id))

    await query.message.edit_media(
        media=book.get_book_photo(FSINPUTFILE=False),
        )
    
    await query.message.edit_caption(
        caption=f"Узнай о книге \"{book.get_book_info('name')}\" больше",
        reply_markup=keyboards.book_info_kb(book.id)
        )

        # book_info_message: str = "\n".join([f"{key}: {value} \n{'-' * 20}" for key, value in book_info.items()])
        
        # await query.message.answer_photo(photo=FSInputFile(photo_path))
        # await query.message.answer(text=book_info_message)


@router.callback_query(keyboards.BookInfo.filter(F.action == "book_info_check"))
async def bookinfo_handler(query: CallbackQuery, callback_data: keyboards.BookInfo):
    book = BookDatabase(int(callback_data.book_id))
    
    info = book.get_book_info(callback_data.column_name)
    await query.message.edit_caption(
        caption=info,
        reply_markup=keyboards.book_info_additions_kb(book.id))
        

@router.callback_query(keyboards.BookInfo.filter(F.action == "return_back_to_info"))
async def bookinfo_back_to_info_handler(query: CallbackQuery, callback_data: keyboards.BookInfo):
    book = BookDatabase(int(callback_data.book_id))
    await query.message.edit_caption(
        caption=f"Узнай о книге \"{book.get_book_info('name')}\" больше",
        reply_markup=keyboards.book_info_kb(book_id=callback_data.book_id)
    )


@router.callback_query(keyboards.BookInfo.filter(F.action == "return_back"))
async def bookinfo_back_handler(query: CallbackQuery, callback_data: keyboards.BookList):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(all_books_image_path))
        )
    await query.message.edit_caption(
        caption=f"Мы рекомендуем вам эти книги",
        reply_markup=keyboards.all_books_kb())

