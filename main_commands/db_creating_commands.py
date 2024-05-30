from aiogram.filters import Command, CommandObject
from aiogram import Router
from aiogram.types import Message
import sqlite3

from utils.database import BookDatabase, AdminDatabase, InfoDatabase


router = Router()


@router.message(Command("db_create"))
async def db_create(message: Message, command: CommandObject):
    '''Создает базу данных'''
    if AdminDatabase.get_admin_level(message.from_user.id) >= 1:
        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            # cursor.execute("DROP TABLE admins")
            AdminDatabase.renew_table()
            BookDatabase.renew_table()
            InfoDatabase.renew_table()

            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS schedule (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        description TEXT,
                        day DATE,
                        time TIME,
                        expired INTEGER,
                        group_id INTEGER
                        )""")
            
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tg_id INTEGER UNIQUE,
                        username TEXT,
                        is_subscribed INTEGER,
                        date_of_subscription DATETIME,
                        date_of_unsubscription DATETIME
                        )""")
            
        