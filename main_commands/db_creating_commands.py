from aiogram.filters import Command, CommandObject
from aiogram import Router
from aiogram.types import Message
import sqlite3


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
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS schedule (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       description TEXT,
                       day DATE,
                       time TIME,
                       expired INTEGER
                       )""")
        
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS books (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT,
                       description TEXT,
                       author CHAR,
                       genre CHAR,
                       year INTEGER,
                       publishing_house CHAR,
                       rating REAL,
                       age_rating CHAR,
                       image BLOB DEFAULT NULL
                       )""")
        