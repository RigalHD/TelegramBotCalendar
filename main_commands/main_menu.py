from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import CallbackQuery, FSInputFile
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from config import *
from all_keyboards import inline_keyboards
from .states import (
    MeetingsForm, 
    BooksForm, 
    AddInfoForm, 
    ChangeInfoForm, 
    RemoveInfoForm,
    ProfileChangeNameForm,
    ProfileChangeDescriptionForm, 
)

from utils.database import (
    AdminDatabase, 
    InfoDatabase, 
    SchedulerDatabase, 
    ProfilesDatabase
    )

router = Router()


@router.callback_query(inline_keyboards.MainMenu.filter(F.action == "Books_view"))
async def books_view_handler(query: CallbackQuery, callback_data: inline_keyboards.MainMenu):
    # await query.message.edit_media(
    #     media=InputMediaPhoto(media=FSInputFile(all_books_image_path)),
    # )
    await query.message.edit_caption(
        caption="Просмотр книг",
        reply_markup=inline_keyboards.books_kb()
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


@router.callback_query(inline_keyboards.InfoView.filter(F.action == "Schedule_check"))
async def schedule_check_handler(query: CallbackQuery, callback_data: inline_keyboards.InfoView):
    meeting: SchedulerDatabase = SchedulerDatabase.get_actual_meeting()
    info_message = f"""Информация о следующей встрече книжного клуба:
        Что на ней будет? - <b>{meeting.description}</b>
        Когда она будет? - <b>{meeting.date_time.date().strftime("%d.%m.%y")}</b>
        Во сколько приходить? - <b>{str(meeting.date_time.time())[:-3]}</b>
        """
    
    await query.message.edit_caption(
        caption=info_message,
        reply_markup=inline_keyboards.back_to_info_kb(
            callback_data.name, 
            query.from_user.id,
            has_info_change_button=False
        )
    )

@router.callback_query(inline_keyboards.ProfileView.filter(F.action == "View_my_profile"))
async def profile_check_handler(query: CallbackQuery, callback_data: inline_keyboards.ProfileView):
    profile: ProfilesDatabase = ProfilesDatabase(query.from_user.id)
    info_message = f"Информация о вашем профиле: \n"\
        f"  • Ваш псевдоним - *{profile.name if profile.name else query.from_user.first_name}* \n"\
        f"  • Когда вы создали профиль - *{profile.join_date}* \n"\
        f"  • Ваш телеграм id - *{profile.telegram_id}* \n"\
        f"  • Ваша биография: \n{profile.bio}"
    
    await query.message.edit_caption(
        caption=info_message,
        reply_markup=inline_keyboards.profile_view_kb(),
        parse_mode="Markdown"
    )


@router.callback_query(inline_keyboards.ProfileView.filter(F.action == "Change_name"))
async def change_profile_name_handler(query: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileChangeNameForm.name)
    await query.message.answer(text="Введите новый псевдоним: ")


@router.callback_query(inline_keyboards.ProfileView.filter(F.action == "Change_bio"))
async def change_profile_bio_handler(query: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileChangeDescriptionForm.bio)
    await query.message.answer(text="Введите новую биографию: ")


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
        reply_markup=inline_keyboards.admin_panel_kb(query.from_user.id)
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
