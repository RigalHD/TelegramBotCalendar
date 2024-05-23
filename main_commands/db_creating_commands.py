from aiogram.filters import Command, CommandObject
from aiogram import Router
from aiogram.types import Message
import sqlite3

from utils.database import BookDatabase, AdminDatabase


router = Router()


@router.message(Command("db_create"))
async def db_create(message: Message, command: CommandObject):
    '''Создает базу данных'''
    if not AdminDatabase.is_admin(message.from_user.id):
        await message.answer(text="Отказано в доступе")
        return
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        # cursor.execute("DROP TABLE schedule")
        
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS schedule (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       description TEXT,
                       day DATE,
                       time TIME,
                       expired INTEGER,
                       group_id INTEGER
                       )""")
        
        BookDatabase.create_if_not_exists()
        
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS users(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       tg_id INTEGER UNIQUE,
                       username TEXT,
                       is_subscribed INTEGER,
                       date_of_subscription DATETIME,
                       date_of_unsubscription DATETIME
                       )""")