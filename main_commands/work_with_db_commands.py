from aiogram.filters import Command, CommandObject
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
import sqlite3
import datetime
from all_keyboards import keyboards
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from all_keyboards.keyboards import book_age_rating_kb
from aiogram.types import ReplyKeyboardRemove
from main import bot, send_reminder


router = Router()


class BooksForm(StatesGroup):
    name = State()
    description = State()
    author = State()
    genre = State()
    year = State()
    publishing_house = State()
    rating = State()    
    age_rating = State()
    image = State()


@router.message(Command("add_book"))
async def db_add_book(message: Message, state: FSMContext) -> None:
    '''Добавление книги в базу данных'''
    if message.from_user.id != 997987348:
        await message.answer(text="Отказано в доступе")
        return
    await state.set_state(BooksForm.name)
    await message.answer(text="Введите название книги: ")


@router.message(BooksForm.name)
async def process_book_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(BooksForm.description)
    await message.answer(text="ок. теперь введите описание: ")


@router.message(BooksForm.description)
async def process_book_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(BooksForm.author)
    await message.answer(text="ок. теперь введите автора: ")


@router.message(BooksForm.author)
async def process_book_author(message: Message, state: FSMContext) -> None:
    await state.update_data(author=message.text)
    await state.set_state(BooksForm.genre)
    await message.answer(text="ок. теперь введите жанр: ")


@router.message(BooksForm.genre)
async def process_book_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text)
    await state.set_state(BooksForm.year)
    await message.answer(text="ок. теперь введите год: ")
    

@router.message(BooksForm.year)
async def process_book_year(message: Message, state: FSMContext) -> None:
    try:
        await state.update_data(year=int(message.text))
    except ValueError:
        await message.answer("Некорректный год")
        return
    await state.set_state(BooksForm.publishing_house)
    await message.answer(text="ок. теперь введите издательство: ")

 
@router.message(BooksForm.publishing_house)
async def process_book_publishing_house(message: Message, state: FSMContext) -> None:
    await state.update_data(publishing_house=message.text)
    await state.set_state(BooksForm.rating)
    await message.answer(text="ок. теперь введите рейтинг книги: ")
    

@router.message(BooksForm.rating)
async def process_book_rating(message: Message, state: FSMContext) -> None:
    try:
        await state.update_data(rating=float(message.text))
    except ValueError:
        await message.answer("Некорректный рейтинг")
        return
    await state.set_state(BooksForm.age_rating)
    await message.answer(text="ок. теперь выберите возрастной рейтинг картинки ", reply_markup=book_age_rating_kb())


@router.message(BooksForm.age_rating)
async def process_book_age_rating(message: Message, state: FSMContext) -> None:
    if message.text not in ("7-10", "10-14", "14-18"):
        await message.answer(text="Некорректный возрастной рейтинг")
        return
    await state.update_data(age_rating=message.text)
    await state.set_state(BooksForm.image)
    await message.answer(text="ок. теперь загрузите сюда картинку с обложкой книги: ", reply_markup=ReplyKeyboardRemove())
    

@router.message(BooksForm.image)
async def process_book_image(message: Message, state: FSMContext) -> None:
    if message.photo:
        file_info = await bot.get_file(message.photo[-1].file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        try:
            src = "bot_images/" + message.photo[-1].file_id + ".jpg"  # Если у вас есть проблемы с этой строкой, то создайте в папке проекта папку bot_images/
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file.getvalue())

            with open(src, 'rb') as new_file:
                await state.update_data(image=new_file.read())
            await state.update_data(image=src)
            
            data = await state.get_data()
            await state.clear()

            full_data = (
                data["name"], data["description"], data["author"], data["genre"], int(data["year"]), 
                data["publishing_house"], float(data["rating"]), data["age_rating"], data["image"]
                )

            with sqlite3.connect("db.db") as db:
                cursor = db.cursor()
                cursor.execute("""
                                INSERT INTO books (
                                name, description, author, genre, year, 
                                publishing_house, rating, age_rating, image) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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


@router.message(Command("Подписаться_на_рассылку"))
async def db_subscribe_to_the_newsletter(message: Message):
    '''
    Эта команда позволяет подписаться
    на рассылку встреч книжного клуба
    '''
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        user_data = (
            message.from_user.id,
            message.from_user.username,
            1,
            datetime.datetime.now()
            )
        all_users_ids = cursor.execute("SELECT tg_id FROM users").fetchall()
        if all_users_ids:
            for id in all_users_ids:
                if not message.from_user.id in id:
                    cursor.execute("""INSERT INTO users (
                    tg_id,
                    username, 
                    is_subscribed, 
                    date_of_subscription
                    ) VALUES (?, ?, ?, ?)""",
                    user_data 
                    )
                    await message.answer(text="Вы успешно подписались на рассылку")
                    return
        await message.answer(text="Вы уже подписаны на рассылку")
    

class Form(StatesGroup):
    description = State()
    day = State()
    time = State()
    group_id = State() # временное решение


@router.message(Command("db_add_meet"))
async def db_add_meet(message: Message, state: FSMContext) -> None:
    '''Добавление в расписание новую встречу'''
    if message.from_user.id != 997987348:
        await message.answer(text="Отказано в доступе")
        return
    await state.set_state(Form.description)
    await message.answer(text="Введите описание: ")


@router.message(Form.description)
async def process_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(Form.day)
    await message.answer(text="ок. теперь введите день: ")


@router.message(Form.day)
async def process_day(message: Message, state: FSMContext) -> None:
    await state.update_data(day=message.text)
    await state.set_state(Form.time)
    await message.answer(text="ок. теперь введите время: ")
    

@router.message(Form.time)
async def process_time(message: Message, state: FSMContext) -> None:
    await state.update_data(time=message.text)
    await state.set_state(Form.group_id)
    await message.answer(text="ок. теперь введите айди нужной группы: ")


@router.message(Form.group_id)
async def process_group_id(message: Message, state: FSMContext) -> None:
    await state.update_data(group_id=message.text)
    await message.answer(text="ок. ")
    data = await state.get_data()
    await state.clear()
    full_data = list(data.values())
    full_data[2] = data["time"] + ":00"
    group_id = full_data[-1]
    full_data[-1] = 0
    full_data.append(group_id)
    
    await message.answer(text=str(data), parse_mode=None)
    hour, minute = [int(i) for i in data["time"].split(":")]
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute("""
                       INSERT INTO schedule (
                       description,
                       day, 
                       time, 
                       expired,
                       group_id
                       ) VALUES (?, ?, ?, ?, ?)""",
                       full_data
                       )
        
        info_message = f"""Внимание! Напоминаем о встрече книжного клуба!
        Что на ней будет? - <b>{data["description"]}</b>
        Когда она будет? - <b>{hour}:{minute}</b>
        Во сколько приходить? - <b>{data["time"]}</b> """


        users_ids = cursor.execute("SELECT tg_id FROM users WHERE is_subscribed = 1").fetchall()

        scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
        scheduler.add_job(
            send_reminder, 'cron',
            hour=int(hour),
            minute=int(minute), 
            start_date=datetime.datetime.now(), # ЗАМЕНИТЬ НА НУЖНУЮ ДАТУ ПОТОМ!!!!!!!!!!!!!!!!!!!!!!
            kwargs={
                "bot": bot,
                "users_id": users_ids,
                "info_message": info_message,
                "group_id": group_id
                },
        )

        scheduler.start()


@router.message(Command("test_kb"))
async def call_test_kb(message: Message, command: CommandObject):
    '''Вызывает тестовую клавиатуру'''
    if message.from_user.id != 997987348:
        await message.answer(text="Отказано в доступе")
        return
    await message.answer(
    f"Test kb of books, <b>{message.from_user.first_name}</b>",
    reply_markup=keyboards.all_books_kb())