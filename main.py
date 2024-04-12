import asyncio
import all_keyboards.keyboards as keyboards
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from cfgs import TOKEN
from main_commands import user_commands, work_with_db
from config import GROUP_ID
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime


bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())


async def send_msg(bot: Bot):
    await bot.send_message(4153686151, "OK!")


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Приветствую, <b>{message.from_user.first_name}</b>",
        reply_markup=keyboards.main_kb(message.from_user.id))
    await message.answer(f"Ваш айди -> {message.from_user.id}")


async def send_reminder(bot: Bot, users_id: int, info_message: str):
    await bot.send_message(chat_id=GROUP_ID, text=info_message)
    for user_id in users_id:
        await bot.send_message(chat_id=user_id[0], text=info_message)


async def sender_of_reminds(bot: Bot):
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            username TEXT,
            is_subscribed INTEGER,
            date_of_subscription DATETIME,
            date_of_unsubscription DATETIME
        )""")
        users_ids = cursor.execute("SELECT tg_id FROM users WHERE is_subscribed = 1").fetchall()
        scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
        data = cursor.execute("SELECT * FROM schedule WHERE expired = 0").fetchone()
        hour, minute = data[3].split(":")[:-1]

        info_message = f"""Внимание! Напоминаем о встрече книжного клуба!
        Что на ней будет? - <b>{data[1]}</b>
        Когда она будет? - <b>{hour}:{minute}</b>
        Во сколько приходить? - <b>{data[2]}</b> """

        scheduler.add_job(
            send_reminder, 'cron',
            hour=int(hour),
            minute=int(minute), 
            start_date=datetime.now(), # ЗАМЕНИТЬ НА НУЖНУЮ ДАТУ ПОТОМ!!!!!!!!!!!!!!!!!!!!!!
            kwargs={"bot": bot, "users_id": users_ids, "info_message": info_message},
            id="main_job"
            )
        
        return scheduler


async def main():
    dp.include_routers(
        user_commands.router,
        work_with_db.router,
    )
    sch = await sender_of_reminds(bot)
    sch.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
