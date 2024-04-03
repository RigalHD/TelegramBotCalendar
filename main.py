import asyncio
import all_keyboards.keyboards as keyboards
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from cfgs import TOKEN
from main_commands import user_commands, work_with_db

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime


bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())


async def send_msg(bot: Bot):
    await bot.send_message(997987348, "OK!")


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Приветствую, <b>{message.from_user.first_name}</b>",
        reply_markup=keyboards.main_keyboard)
    await message.answer(f"Ваш айди -> {message.from_user.id}")


async def send_reminder(bot: Bot, user_id: int):
    await bot.send_message(user_id, "Напоминание")


async def sender_of_reminds(bot: Bot):
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            username TEXT,
            is_subscribed INTEGER,
            date_of_subscription DATETIME,
            date_of_unsubscription DATETIME
        )""")
        users_ids = cursor.execute("SELECT tg_id FROM users WHERE is_subscribed = 1").fetchall()
        # print(users_ids)
        # print(users_count)
        # print(cursor.execute("SELECT * FROM users").fetchall())
        scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
        data = cursor.execute("SELECT * FROM schedule").fetchone()
        hour, minute = data[3].split(":")[:-1]
        # print(hour, minute)
        # print(data)
        for i in range(len(users_ids)):
            scheduler.add_job(
                send_reminder, 'cron',
                second=minute, # second = минута, minute = час
                minute=hour,
                start_date=datetime.now(), # ЗАМЕНИТЬ НА НУЖНУЮ ДАТУ ПОТОМ!!!!!!!!!!!!!!!!!!!!!!
                kwargs={"bot": bot, "user_id": users_ids[i]},
                id=f"main_job_{i}"
                )
        return scheduler


async def main():
    dp.include_routers(
        user_commands.router,
        work_with_db.router,
    )

    scheduler = await sender_of_reminds(bot)
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
