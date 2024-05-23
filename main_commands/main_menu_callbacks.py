from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import CallbackQuery, FSInputFile
from aiogram import Router, F

from config import *
from all_keyboards import inline_keyboards

router = Router()


@router.callback_query(inline_keyboards.MainMenu.filter(F.action == "Books_view"))
async def books_view_handler(query: CallbackQuery, callback_data: inline_keyboards.BookInfo):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(all_books_image_path)),
    )
    await query.message.edit_caption(
        caption="Мы рекомендуем вам эти книги",
        reply_markup=inline_keyboards.all_books_kb()
    )


@router.callback_query(inline_keyboards.MainMenu.filter(F.action == "Info_view"))
async def info_view_handler(query: CallbackQuery, callback_data: inline_keyboards.BookInfo):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(info_image_path)),
        
    )
    await query.message.edit_caption(
        caption="Информация",
        reply_markup=inline_keyboards.info_view_kb()
    )


@router.callback_query(inline_keyboards.InfoView.filter(F.action == "Return_to_info_view"))
async def return_to_main_menu_handler(query: CallbackQuery, callback_data: inline_keyboards.BookInfo):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(info_image_path)),
    )
    await query.message.edit_caption(
        caption="Информация",
        reply_markup=inline_keyboards.info_view_kb()
    )


@router.callback_query(inline_keyboards.MainMenu.filter(F.action == "Return_to_main_menu"))
async def return_to_main_menu_handler(query: CallbackQuery, callback_data: inline_keyboards.BookInfo):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(main_menu_image_path)),
    )
    await query.message.edit_caption(
        caption="Главное меню",
        reply_markup=inline_keyboards.main_menu_kb(query.from_user.id)
    )

