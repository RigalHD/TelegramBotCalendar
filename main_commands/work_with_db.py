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

router = Router()


@router.message(Command("db_create"))
async def db_create(message: Message, command: CommandObject):
    '''Создает базу данных'''
    if message.from_user.id != 997987348:
        await message.answer(text="Отказано в доступе")
        return
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute("DROP TABLE schedule")
        cursor.execute("""CREATE TABLE IF NOT EXISTS schedule (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       description TEXT,
                       day DATE,
                       time TIME,
                       expired INTEGER
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
async def process_description(message: Message, state: FSMContext) -> None:
    await state.update_data(day=message.text)
    await state.set_state(Form.time)
    await message.answer(text="ок. теперь введите время: ")
    

@router.message(Form.time)
async def process_description(message: Message, state: FSMContext) -> None:
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
