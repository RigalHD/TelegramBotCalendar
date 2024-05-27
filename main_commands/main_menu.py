from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.filters import Command, CommandObject
from aiogram import Router, F
import sqlite3
from config import *
from all_keyboards import inline_keyboards
from .work_with_db_commands import Form
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from main import dp
import datetime
from utils.database import AdminDatabase

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


@router.callback_query(inline_keyboards.MainMenu.filter(F.action == "Admin_panel_view"))
async def admin_panel_handler(query: CallbackQuery, callback_data: inline_keyboards.AdminPanel):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(admin_panel_image_path)),
    )
    await query.message.edit_caption(
        caption="Админ панель",
        reply_markup=inline_keyboards.admin_panel_kb(callback_data.user_id)
    )


@router.callback_query(inline_keyboards.AdminPanel.filter(F.action == "Add_meeting"))
async def add_meeting_handler(query: CallbackQuery, state: FSMContext):
    await state.set_state(Form.description)
    await query.message.answer("Введите описание:")


@router.callback_query(inline_keyboards.MainMenu.filter(F.action == "Return_to_main_menu"))
async def return_to_main_menu_handler(query: CallbackQuery, callback_data: inline_keyboards.MainMenu):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(main_menu_image_path)),
    )
    await query.message.edit_caption(
        caption="Главное меню",
        reply_markup=inline_keyboards.main_menu_kb(query.from_user.id)
    )

