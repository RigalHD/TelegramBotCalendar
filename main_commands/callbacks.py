from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import CallbackQuery, FSInputFile
from aiogram import Router, F

from utils.database import BookDatabase
from config import all_books_image_path
from all_keyboards import inline_keyboards


router = Router()


@router.callback_query(inline_keyboards.BookList.filter(F.action == "book_check"))
async def booklist_handler(query: CallbackQuery, callback_data: inline_keyboards.BookList):
    book = BookDatabase(int(callback_data.book_id))

    await query.message.edit_media(
        media=book.get_book_photo(FSINPUTFILE=False),
        )
    
    await query.message.edit_caption(
        caption=f"Узнай о книге \"{book.get_book_info('name')}\" больше",
        reply_markup=inline_keyboards.book_info_kb(book.id)
        )

        # book_info_message: str = "\n".join([f"{key}: {value} \n{'-' * 20}" for key, value in book_info.items()])
        
        # await query.message.answer_photo(photo=FSInputFile(photo_path))
        # await query.message.answer(text=book_info_message)


@router.callback_query(inline_keyboards.BookInfo.filter(F.action == "book_description_check"))
async def book_description_handler(query: CallbackQuery, callback_data: inline_keyboards.BookInfo):
    book = BookDatabase(int(callback_data.book_id))
    info = book.get_book_info('description')
    await query.message.edit_caption(
        caption=info,
        reply_markup=inline_keyboards.book_info_additions_kb(book.id))
    

@router.callback_query(inline_keyboards.BookInfo.filter(F.action == "book_additional_info_check"))
async def book_addditional_info_handler(query: CallbackQuery, callback_data: inline_keyboards.BookInfo):
    book = BookDatabase(int(callback_data.book_id))
    
    info = "\n" + ("-" * 20) + "\n" + "\n".join(
        [f"{key}: {value} \n{'-' * 20}" for key, value in book.get_full_book_info(
            has_name=False,
            has_description=False,
            has_rus_copolumns=True
            ).items()]
        )
    await query.message.edit_caption(
        caption="Дополнительная информация о книге: \n" + info,
        reply_markup=inline_keyboards.book_info_additions_kb(book.id))


@router.callback_query(inline_keyboards.BookInfo.filter(F.action == "return_back_to_info"))
async def bookinfo_back_to_info_handler(query: CallbackQuery, callback_data: inline_keyboards.BookInfo):
    book = BookDatabase(int(callback_data.book_id))
    await query.message.edit_caption(
        caption=f"Узнай о книге \"{book.get_book_info('name')}\" больше",
        reply_markup=inline_keyboards.book_info_kb(book_id=callback_data.book_id)
    )


@router.callback_query(inline_keyboards.BookInfo.filter(F.action == "return_back"))
async def bookinfo_back_handler(query: CallbackQuery, callback_data: inline_keyboards.BookList):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(all_books_image_path))
        )
    await query.message.edit_caption(
        caption=f"Мы рекомендуем вам эти книги",
        reply_markup=inline_keyboards.all_books_kb())
