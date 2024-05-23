from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.filters import Command, CommandObject
from aiogram import Router, F

from config import *
from all_keyboards import inline_keyboards

router = Router()

# @router.message(Command("view_random_books"))
# async def view_random_books(message: Message, command: CommandObject):
#     if not AdminDatabase.is_admin(message.from_user.id):
#         await message.answer(text="Отказано в доступе")
#         return
#     await message.answer_photo(
#     photo=FSInputFile(all_books_image_path),
#     caption=f"Мы рекомендуем вам эти книги",
#     reply_markup=inline_keyboards.all_books_kb())

@router.callback_query(inline_keyboards.MainMenu.filter(F.action == "Books_view"))
async def books_view_handler(query: CallbackQuery, callback_data: inline_keyboards.MainMenu):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(all_books_image_path)),
    )
    await query.message.edit_caption(
        caption="Мы рекомендуем вам эти книги",
        reply_markup=inline_keyboards.all_books_kb()
    )


@router.callback_query(inline_keyboards.MainMenu.filter(F.action == "Info_view"))
async def info_view_handler(query: CallbackQuery, callback_data: inline_keyboards.MainMenu):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(info_image_path)),
        
    )
    await query.message.edit_caption(
        caption="Информация",
        reply_markup=inline_keyboards.info_view_kb()
    )


@router.callback_query(inline_keyboards.InfoView.filter(F.action == "Info_check"))
async def info_check_handler(query: CallbackQuery, callback_data: inline_keyboards.InfoView):
    await query.message.edit_caption(
        caption=callback_data.description,
        reply_markup=inline_keyboards.back_to_info_kb()
    )


@router.callback_query(inline_keyboards.InfoView.filter(F.action == "Return_to_info_view"))
async def return_to_info_view_handler(query: CallbackQuery, callback_data: inline_keyboards.InfoView):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(info_image_path)),
    )
    await query.message.edit_caption(
        caption="Информация",
        reply_markup=inline_keyboards.info_view_kb()
    )


@router.callback_query(inline_keyboards.MainMenu.filter(F.action == "Return_to_main_menu"))
async def return_to_main_menu_handler(query: CallbackQuery, callback_data: inline_keyboards.MainMenu):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(main_menu_image_path)),
    )
    await query.message.edit_caption(
        caption="Главное меню",
        reply_markup=inline_keyboards.main_menu_kb(query.from_user.id)
    )

