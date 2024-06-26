from aiogram.filters import Command, CommandObject
from aiogram import Router
from aiogram.types import Message
import sqlite3

from utils.database import (
    BookDatabase,
    AdminDatabase, 
    InfoDatabase, 
    SchedulerDatabase,
    ProfilesDatabase
    )


router = Router()


@router.message(Command("db_create"))
async def db_create(message: Message, command: CommandObject):
    '''Создает базу данных'''
    if AdminDatabase.is_admin(message.from_user.id):
        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            # cursor.execute("DROP TABLE books")
            # cursor.execute("DROP TABLE schedule")
            AdminDatabase.renew_table()
            BookDatabase.renew_table()
            InfoDatabase.renew_table()
            SchedulerDatabase.renew_table()
            ProfilesDatabase.renew_table()


@router.message(Command("get_chat_id"))
async def get_chat_id(message: Message, command: CommandObject):
    '''Создает базу данных'''
    if AdminDatabase.is_admin(message.from_user.id):
        print(message.chat.id)
