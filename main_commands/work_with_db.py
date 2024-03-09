from aiogram.filters import Command, CommandObject
from aiogram import Bot, Router, F
from aiogram.types import Message
import sqlite3
from datetime import datetime

router = Router()

@router.message(Command("db_create"))
async def db_create(message: Message, command: CommandObject):
    '''Создает базу данных'''
    if message.from_user.id != 997987348:
        await message.answer(text="Отказано в доступе")
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS schedule (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       description TEXT,
                       day DATE,
                       time TIME
                       )""")


@router.message(Command("db_add_meet"))
async def db_add_meet(message: Message, command: CommandObject):
    '''Добавление в расписание встреч новую'''
    if message.from_user.id != 997987348:
        await message.answer(text="Отказано в доступе")
    if not command.args:
        await message.answer(
            text=\
            "Добавьте встречу вот так: \n/db_add_meet <Дата (пример: 01.01.2024)> <Время> (пример: 12:00)", 
            # Добавить потом: <Описание встречи (вкратце о том, что на ней будет)>
            parse_mode=None)
        return
    print(command.args)
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute("""INSERT INTO schedule (
                       description, day, time)
                       VALUES (?, ?, ?)""", ("-", *command.args.split()))
        print(cursor.execute("""SELECT * FROM schedule""").fetchall())

