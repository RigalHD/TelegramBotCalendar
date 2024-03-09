from aiogram.filters import Command, CommandObject
from aiogram import Bot, Router, F
from aiogram.types import Message
import sqlite3


router = Router()

@router.message(Command("db_test"))
async def command_test(message: Message, command: CommandObject):
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS schedule (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name CHAR,
                       description TEXT,
                       day DATE,
                       time TIME
                       )""")
        