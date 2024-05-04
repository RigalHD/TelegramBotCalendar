from aiogram.types import CallbackQuery
from all_keyboards import keyboards
from aiogram import Router, F

from utils.database import BookDatabase

router = Router()


@router.callback_query(keyboards.BookList.filter(F.action == "book_check"))
async def booklist_handler(query: CallbackQuery, callback_data: keyboards.BookList):
    book = BookDatabase(int(callback_data.book_id))

    await query.message.edit_media(
        media=book.get_book_photo(FSINPUTFILE=False),
        )
    
    await query.message.edit_caption(
        caption="Узнай о книге больше",
        reply_markup=keyboards.book_info_kb(book.id)
        )

        # book_info_message: str = "\n".join([f"{key}: {value} \n{'-' * 20}" for key, value in book_info.items()])
        
        # await query.message.answer_photo(photo=FSInputFile(photo_path))
        # await query.message.answer(text=book_info_message)


@router.callback_query(keyboards.BookInfo.filter(F.action == "book_info_check"))
async def bookinfo_handler(query: CallbackQuery, callback_data: keyboards.BookList):
    book = BookDatabase(int(callback_data.book_id))
    
    info = book.get_book_info(callback_data.column_name)
    await query.message.edit_caption(
        caption=info,
        reply_markup=keyboards.book_info_additions_kb(book.id))
        

@router.callback_query(keyboards.BookInfo.filter(F.action == "return_back_to_info"))
async def bookinfo_back_to_info_handler(query: CallbackQuery, callback_data: keyboards.BookList):
    book = BookDatabase(int(callback_data.book_id))
    await query.message.edit_caption(
        caption="Узнай о книге больше",
        reply_markup=keyboards.book_info_kb(book_id=book.id)
    )
