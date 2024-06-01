from aiogram import Router
from aiogram.types import Message
import sqlite3
import datetime
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from all_keyboards.keyboards import book_age_rating_kb
from aiogram.types import ReplyKeyboardRemove
from main import bot, send_reminder
from utils.database import InfoDatabase, SchedulerDatabase
import os

router = Router()


class BooksForm(StatesGroup):
    name = State()
    description = State()
    author = State()
    genre = State()
    year = State()
    film_adaptations = State()
    age_rating = State()
    image = State()


# @router.message(Command("add_book"))
# async def db_add_book(message: Message, state: FSMContext) -> None:
#     '''Добавление книги в базу данных'''
#     if not AdminDatabase.is_admin(message.from_user.id):
#         await message.answer(text="Отказано в доступе")
#         return
#     await state.set_state(BooksForm.name)
#     await message.answer(text="Введите название книги: ")


@router.message(BooksForm.name)
async def process_book_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(BooksForm.description)
    await message.answer(text="Введите описание книги: ")


@router.message(BooksForm.description)
async def process_book_description(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1024:
        await message.answer(
            text="Описание книги слишком длинное.\n"
            "Описание должно быть меньше или равно 1024 символам.\n"
            "Введите другое описание книги:"
            )
        return
    await state.update_data(description=message.text)
    await state.set_state(BooksForm.author)
    await message.answer(text="Введите автора книги: : ")


@router.message(BooksForm.author)
async def process_book_author(message: Message, state: FSMContext) -> None:
    await state.update_data(author=message.text)
    await state.set_state(BooksForm.genre)
    await message.answer(text="Введите жанр книги: ")


@router.message(BooksForm.genre)
async def process_book_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text)
    await state.set_state(BooksForm.year)
    await message.answer(text="Введите год, когда книга была выпущена (Пример: 2024): ")
    

@router.message(BooksForm.year)
async def process_book_year(message: Message, state: FSMContext) -> None:
    try:
        await state.update_data(year=int(message.text))
    except ValueError:
        await message.answer("Некорректный год\nВведите год по такому формату: 2024 ")
        return
    await state.set_state(BooksForm.film_adaptations)
    await message.answer(text="Введите фильмовые адаптации книг: ")

 
@router.message(BooksForm.film_adaptations)
async def process_book_film_adaptations(message: Message, state: FSMContext) -> None:
    await state.update_data(film_adaptations=message.text)
    await state.set_state(BooksForm.age_rating)
    await message.answer(
        text="У вас появилась клавиатура.\n"
        "Выберите в ней возрастной рейтинг.\n"
        "Если по каким-либо причинам Вы не можете воспользоваться клавиатурой, "
        "то отправьте возрастной рейтинг, выбрав его отсюда: <b>7-10, 10-14, 14-18</b>",
        reply_markup=book_age_rating_kb()
        )
    

# @router.message(BooksForm.rating)
# async def process_book_rating(message: Message, state: FSMContext) -> None:
#     try:
#         await state.update_data(rating=float(message.text))
#     except ValueError:
#         await message.answer("Некорректный рейтинг")
#         return
#     await state.set_state(BooksForm.age_rating)
#     await message.answer(text="ок. теперь выберите возрастной рейтинг картинки ", reply_markup=book_age_rating_kb())


@router.message(BooksForm.age_rating)
async def process_book_age_rating(message: Message, state: FSMContext) -> None:
    if message.text not in ("7-10", "10-14", "14-18"):
        await message.answer(text="Некорректный возрастной рейтинг")
        return
    await state.update_data(age_rating=message.text)
    await state.set_state(BooksForm.image)
    await message.answer(text=
                         "Теперь отправьте боту файл с обложкой книги или просто загрузите фото: ", 
                         reply_markup=ReplyKeyboardRemove()
                         )
    

@router.message(BooksForm.image)
async def process_book_image(message: Message, state: FSMContext) -> None:
    if message.photo:
        file_info = await bot.get_file(message.photo[-1].file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        try:
            if not os.path.isdir("bot_images/"):
                os.makedirs("bot_images/")
            src = "bot_images/" + message.photo[-1].file_id + ".jpg"  # Если у вас есть проблемы с этой строкой, то создайте в папке проекта папку bot_images/
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file.getvalue())

            await state.update_data(image=src)
            
            data = await state.get_data()
            await state.clear()

            full_data = (
                data["name"], data["description"], data["author"], data["genre"], int(data["year"]), 
                data["film_adaptations"], data["age_rating"], data["image"]
                )

            with sqlite3.connect("db.db") as db:
                cursor = db.cursor()
                cursor.execute("""
                                INSERT INTO books (
                                name, description, author, genre, year, 
                                film_adaptations, age_rating, image) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                               """,
                               full_data
                )
                await message.answer(text="Книга успешно добавлена")

        except FileNotFoundError as e:
            await message.answer(text="Ошибка при загрузке картинки. Обратитесь к администрации бота BooksClubBot")
            with open("FileNotFoundErrors.txt", "A+") as file:
                file.write(f"{e} - {datetime.datetime.now()}")
                file.write("\n")

        except ValueError:
            await message.answer(text="Ошибка при заполнении полей")
            return


class MeetingsForm(StatesGroup):
    description = State()
    day = State()
    time = State()


# @router.message(Command("db_add_meet"))
# async def db_add_meet(message: Message, state: FSMContext) -> None:
#     '''Добавление в расписание новую встречу'''
#     if not AdminDatabase.is_admin(message.from_user.id):
#         await message.answer(text="Отказано в доступе")
#         return
#     await state.set_state(MeetingsForm.description)
#     await message.answer(text="Введите описание встречи: ")


@router.message(MeetingsForm.description)
async def process_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(MeetingsForm.day)
    now = datetime.datetime.today().date().strftime("%d.%m.%Y")
    await message.answer(text=f"Введите дату встречи по примеру <b>{now}</b>: ")


@router.message(MeetingsForm.day)
async def process_day(message: Message, state: FSMContext) -> None:
    try:
        data = [int(el) for el in message.text.replace("-", ".").replace(",", ".").split(".")]
        data = datetime.date(day=data[0], month=data[1], year=data[2])
        for meeting in SchedulerDatabase.get_schedule():
            if data == meeting.date_time.date():
                await message.answer(text="На этот день уже назначена встреча книжного клуба")
                return
        if data < datetime.date.today():
            await message.answer(text="Мы пока не изобрели машину времени")
            return
    except ValueError:
        await message.answer(text="Неверный формат даты")
        return
    except IndexError:
        await message.answer(text="Неверный формат даты")
        return
    await state.update_data(day=message.text)
    await state.set_state(MeetingsForm.time)
    await message.answer(text="Введите время встречи по примеру <b>12:01</b>: ")
    

@router.message(MeetingsForm.time)
async def process_time(message: Message, state: FSMContext) -> None:
    try:
        time = [int(el) for el in message.text.replace(".", ":").split(":")]
        time = datetime.time(hour=time[0], minute=time[1])
        date = await state.get_data()
        date = [int(el) for el in date["day"].replace("-", ".").replace(",", ".").split(".")]
        date = datetime.date(day=date[0], month=date[1], year=date[2])
        if date == datetime.date.today() and time < datetime.datetime.now().time():
            await message.answer(text="Мы пока не изобрели машину времени, перемещающую на несколько часов назад")
            return
    except ValueError:
        await message.answer(text="Неверный формат времени")
        return
    except IndexError:
        await message.answer(text="Неверный формат времени")
        return
    await state.update_data(time=message.text)

    data = await state.get_data()
    data["time"] = data["time"][:-3]
    await state.clear()
    if SchedulerDatabase.add_meeting(tuple(data.values()), send_reminder):
        await message.answer(text="Встреча успешно добавлена")
    else:
        await message.answer(text="Возникла ошибка")


class AddInfoForm(StatesGroup):
    name = State()
    description = State()


@router.message(AddInfoForm.name)
async def process_info_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(AddInfoForm.description)
    await message.answer(text=f"Введите описание раздела: ")


@router.message(AddInfoForm.description)
async def process_info_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text.replace(":\n", ":   \n").replace("\n",  "\n "))

    data = await state.get_data()
    await state.clear()
    InfoDatabase.renew_table()
    InfoDatabase.add_info(**data)

    await message.answer(text=f"Успешно")


class ChangeInfoForm(StatesGroup):
    name = State()
    description = State()
    # Да, оно на данный момент аналогично AddInfoForm. Если оно не поменяется, то будет удалено


# @router.message(ChangeInfoForm.name)
# async def process_change_info_name(message: Message, state: FSMContext) -> None:
#     if not message.text in InfoDatabase.get_info().keys():
#         await message.answer(text=f"Такого раздела не существует. Введите правильное название раздела")
#         return
#     await state.update_data(name=message.text)
#     await state.set_state(ChangeInfoForm.description)
#     await message.answer(text=f"Введите новое описание раздела: ")


@router.message(ChangeInfoForm.description)
async def process_change_info_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text.replace(":\n", ":   \n").replace("\n",  "\n "))

    data = await state.get_data()
    await state.clear()

    InfoDatabase.update_info(**data)

    await message.answer(text=f"Успешно")


class RemoveInfoForm(StatesGroup):
    name = State()


@router.message(RemoveInfoForm.name)
async def process_remove_info(message: Message, state: FSMContext) -> None:
    if not message.text in InfoDatabase.get_info().keys():
        await message.answer(text=f"Такого раздела не существует. Введите правильное название раздела")
        return
    await state.update_data(name=message.text)
    data = await state.get_data()
    await state.clear()

    InfoDatabase.remove_info(**data)

    await message.answer(text=f"Успешно")
    
