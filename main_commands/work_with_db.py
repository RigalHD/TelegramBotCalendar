from aiogram.filters import Command, CommandObject
from aiogram import Bot, Router
from aiogram.types import Message
import sqlite3
import datetime
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from main import bot, send_reminder
from pprint import pprint

router = Router()


class BooksForm(StatesGroup):
    name = State()
    description = State()
    author = State()
    genre = State()
    year = State()
    publishing_house = State()
    rating = State()
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
    await state.update_data(year=message.text)
    await state.set_state(BooksForm.publishing_house)
    await message.answer(text="ок. теперь введите издательство: ")

 
@router.message(BooksForm.publishing_house)
async def process_book_publishing_house(message: Message, state: FSMContext) -> None:
    await state.update_data(publishing_house=message.text)
    await state.set_state(BooksForm.rating)
    await message.answer(text="ок. теперь введите рейтинг книги: ")
    

@router.message(BooksForm.rating)
async def process_book_rating(message: Message, state: FSMContext) -> None:
    await state.update_data(rating=message.text)
    await state.set_state(BooksForm.image)
    await message.answer(text="ок. теперь загрузите сюда картинку с обложкой книги: ")
    

@router.message(BooksForm.image)
async def process_book_image(message: Message, state: FSMContext) -> None:
    if message.photo:
        file_info = await bot.get_file(message.photo[-1].file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        src = "bot_images/" + message.photo[-1].file_id + ".jpg"  # Если у вас есть проблемы с этой строкой, то создайте в папке проекта папку bot_images/
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file.getvalue())

        with open(src, 'rb') as new_file:
            await state.update_data(image=new_file.read())
        await state.update_data(image=src)
        await message.answer(text="Ок.")
        data = await state.get_data()
        pprint(data)
        await state.clear()

        data["year"] = int(data["year"])
        data["rating"] = float(data["rating"])

        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            cursor.execute("""
                            INSERT INTO books (
                            name, description, author, genre, 
                            year, publishing_house, rating, image) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                           (data["name"], data["description"], data["author"], data["genre"],
                            data["year"], data["publishing_house"], data["rating"], data["image"]))
            print("Запись добавлена")



@router.message(Command("db_create"))
async def db_create(message: Message, command: CommandObject):
    '''Создает базу данных'''
    if message.from_user.id != 997987348:
        await message.answer(text="Отказано в доступе")
        return
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        # cursor.execute("DROP TABLE books")
        cursor.execute("""CREATE TABLE IF NOT EXISTS schedule (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       description TEXT,
                       day DATE,
                       time TIME,
                       expired INTEGER
                       )""")
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS books (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT,
                       description TEXT,
                       author CHAR,
                       genre CHAR,
                       year INTEGER,
                       publishing_house CHAR,
                       rating REAL,
                       image BLOB DEFAULT NULL
                       )""")

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
    await message.answer(text="ок. ")
    data = await state.get_data()
    await state.clear()
    full_data = list(data.values())[:-1]
    full_data.append(data["time"] + ":00")
    full_data.append(0)
    await message.answer(text=str(data), parse_mode=None)

    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute("""
                       INSERT INTO schedule (
                       description,
                       day, 
                       time, 
                       expired
                       ) VALUES (?,?,?,?)""",
                       full_data
                       )
