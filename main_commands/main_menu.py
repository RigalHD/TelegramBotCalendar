from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import CallbackQuery, FSInputFile
from aiogram import Router, F
from config import *
from all_keyboards import inline_keyboards
from .states import MeetingsForm, BooksForm, AddInfoForm, ChangeInfoForm, RemoveInfoForm
from aiogram.fsm.context import FSMContext
from utils.database import AdminDatabase, InfoDatabase

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
        caption=InfoDatabase.get_info()[callback_data.name],
        reply_markup=inline_keyboards.back_to_info_kb(callback_data.name, query.from_user.id),
        parse_mode="Markdown"
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
    if not AdminDatabase.is_admin(query.from_user.id):
        await query.message.answer(text="Отказано в доступе")
        return
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(admin_panel_image_path)),
    )
    await query.message.edit_caption(
        caption="Админ панель",
        reply_markup=inline_keyboards.admin_panel_kb()
    )


@router.callback_query(inline_keyboards.AdminPanel.filter(F.action == "Add_meeting"))
async def add_meeting_handler(query: CallbackQuery, state: FSMContext):
    if not AdminDatabase.is_admin(query.from_user.id):
        await query.message.answer(text="Отказано в доступе")
        return
    await state.set_state(MeetingsForm.description)
    await query.message.answer("Введите описание:")


@router.callback_query(inline_keyboards.AdminPanel.filter(F.action == "Add_book"))
async def add_book_handler(query: CallbackQuery, state: FSMContext):
    if not AdminDatabase.is_admin(query.from_user.id):
        await query.message.answer(text="Отказано в доступе")
        return
    await state.set_state(BooksForm.name)
    await query.message.answer(text="Введите название книги: ")


@router.callback_query(inline_keyboards.AdminPanel.filter(F.action == "Add_info"))
async def add_info_handler(query: CallbackQuery, state: FSMContext):
    if not AdminDatabase.is_admin(query.from_user.id):
        await query.message.answer(text="Отказано в доступе")
        return
    await state.set_state(AddInfoForm.name)
    await query.message.answer(text="Введите название раздела: ")


@router.callback_query(inline_keyboards.InfoView.filter(F.action == "Change_info"))
async def change_info_handler(query: CallbackQuery, state: FSMContext, callback_data: inline_keyboards.InfoView):
    if not AdminDatabase.is_admin(query.from_user.id):
        await query.message.answer(text="Отказано в доступе")
        return
    await state.update_data(name=callback_data.name)
    await state.set_state(ChangeInfoForm.description)
    await query.message.answer(text="Введите описание раздела: ")


@router.callback_query(inline_keyboards.AdminPanel.filter(F.action == "Remove_info"))
async def remove_info_handler(query: CallbackQuery, state: FSMContext):
    if not AdminDatabase.is_admin(query.from_user.id):
        await query.message.answer(text="Отказано в доступе")
        return
    await state.set_state(RemoveInfoForm.name)
    await query.message.answer(text="Введите название раздела для удаления информации: ")


@router.callback_query(inline_keyboards.MainMenu.filter(F.action == "Return_to_main_menu"))
async def return_to_main_menu_handler(query: CallbackQuery, callback_data: inline_keyboards.MainMenu):
    await query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(main_menu_image_path)),
    )
    await query.message.edit_caption(
        caption="Главное меню",
        reply_markup=inline_keyboards.main_menu_kb(query.from_user.id)
    )
