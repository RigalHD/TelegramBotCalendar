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
        await message.answer(message="Отказано в доступе")
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS schedule (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name CHAR,
                       description TEXT,
                       day DATE,
                       time TIME
                       )""")


@router.message(Command("db_add_meet"))
async def db_add_meet(message: Message, command: CommandObject):
    if message.from_user.id != 997987348:
        await message.answer(message="Отказано в доступе")
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()