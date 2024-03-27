from aiogram.filters import Command, CommandObject
from aiogram import Bot, Router, F
from aiogram.types import Message, TelegramObject
import sqlite3
import datetime
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

router = Router()


# import asyncio
# import logging
# import sys
# from os import getenv
# from typing import Any, Dict

# from aiogram import Bot, Dispatcher, F, Router, html
# from aiogram.enums import ParseMode
# from aiogram.filters import Command, CommandStart
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.types import (
#     KeyboardButton,
#     Message,
#     ReplyKeyboardMarkup,
#     ReplyKeyboardRemove,
# )




# class Form(StatesGroup):
#     name = State()
#     like_bots = State()
#     language = State()


# @router.message(F.text == "fff")
# async def comman(message: Message, state: FSMContext) -> None:
#     await state.set_state(Form.name)
#     await message.answer(
#         "Hi there! What's your name?",
#         reply_markup=ReplyKeyboardRemove(),
#     )


# @router.message(Command("cancel"))
# @router.message(F.text.casefold() == "cancel")
# async def cancel_handler(message: Message, state: FSMContext) -> None:
#     """
#     Allow user to cancel any action
#     """
#     current_state = await state.get_state()
#     if current_state is None:
#         return

#     logging.info("Cancelling state %r", current_state)
#     await state.clear()
#     await message.answer(
#         "Cancelled.",
#         reply_markup=ReplyKeyboardRemove(),
#     )


# @router.message(Form.name)
# async def process_name(message: Message, state: FSMContext) -> None:
#     await state.update_data(name=message.text)
#     await state.set_state(Form.name)
#     await message.answer(
#         f"Nice to meet you, {html.quote(message.text)}!\nDid you like to write bots?",
#         reply_markup=ReplyKeyboardMarkup(
#             keyboard=[
#                 [
#                     KeyboardButton(text="Yes"),
#                     KeyboardButton(text="No"),
#                 ]
#             ],
#             resize_keyboard=True,
#         ),
#     )


# @router.message(Form.like_bots, F.text.casefold() == "no")
# async def process_dont_like_write_bots(message: Message, state: FSMContext) -> None:
#     data = await state.get_data()
#     await state.clear()
#     await message.answer(
#         "Not bad not terrible.\nSee you soon.",
#         reply_markup=ReplyKeyboardRemove(),
#     )
#     await show_summary(message=message, data=data, positive=False)


# @router.message(Form.like_bots, F.text.casefold() == "yes")
# async def process_like_write_bots(message: Message, state: FSMContext) -> None:
#     await state.set_state(Form.language)

#     await message.reply(
#         "Cool! I'm too!\nWhat programming language did you use for it?",
#         reply_markup=ReplyKeyboardRemove(),
#     )


# @router.message(Form.like_bots)
# async def process_unknown_write_bots(message: Message) -> None:
#     await message.reply("I don't understand you :(")


# @router.message(Form.language)
# async def process_language(message: Message, state: FSMContext) -> None:
#     data = await state.update_data(language=message.text)
#     await state.clear()

#     if message.text.casefold() == "python":
#         await message.reply(
#             "Python, you say? That's the language that makes my circuits light up! 😉"
#         )

#     await show_summary(message=message, data=data)


# async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True) -> None:
#     name = data["name"]
#     language = data.get("language", "<something unexpected>")
#     text = f"I'll keep in mind that, {html.quote(name)}, "
#     text += (
#         f"you like to write bots with {html.quote(language)}."
#         if positive
#         else "you don't like to write bots, so sad..."
#     )
#     await message.answer(text=text, reply_markup=ReplyKeyboardRemove())

class Form(StatesGroup):
    description = State()
    day = State()
    time = State()

    def __call__(self, event: TelegramObject, raw_state: str | None = None) -> bool:
        return super().__call__(event, raw_state)

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


# @router.message(Command("db_add_meet"))
# async def db_add_meet(message: Message, command: CommandObject):
#     '''Добавление в расписание встреч новую'''
#     if message.from_user.id != 997987348:
#         await message.answer(text="Отказано в доступе")
#     if not command.args:
#         await message.answer(
#             text=\
#             "Добавьте встречу вот так: \n/db_add_meet <Дата (пример: 01.01.2024)> <Время> (пример: 12:00)", 
#             # Добавить потом: <Описание встречи (вкратце о том, что на ней будет)>
#             parse_mode=None)
#         return
    
#     print(command.args)
#     with sqlite3.connect("db.db") as db:
#         cursor = db.cursor()
#         cursor.execute("""INSERT INTO schedule (
#                        description, day, time)
#                        VALUES (?, ?, ?)""", ("-", *command.args.split()))
#         print(cursor.execute("""SELECT * FROM schedule""").fetchall())


@router.message(Command("db_add_meet"))
async def db_add_meet(message: Message, state: FSMContext) -> None:
    '''Добавление в расписание новую встречу'''
    if message.from_user.id != 997987348:
        await message.answer(text="Отказано в доступе")
        return
    # if not command.args:
    #     await message.answer(
    #         text="Добавьте встречу следующим образом:\n/db_add_meet <Дата (пример: 01.01.2024)> <Время (пример: 12:00)>",
    #         parse_mode=None)
    #     return
    await state.set_state(Form.description)
    await message.answer(text="Введите описание: ")
    # print(command.args)


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
    print(datetime.time(data["time"]))
    await message.answer(text=str(data), parse_mode=None)
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute("""INSERT INTO schedule (description, day, time) VALUES (?, ?, ?)""", data.values())
        print(cursor.execute("""SELECT * FROM schedule""").fetchall())

    await state.clear()


