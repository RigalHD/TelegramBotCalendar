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


async def send_reminder(bot: Bot):
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()


    
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
scheduler.add_job(
    send_msg, 'cron',
    second=datetime.now().second + 1, # second = минута, minute = час
    start_date=datetime.now(),
    kwargs={"bot": bot},
    id="main_job"
    )

async def main():
    global scheduler
    scheduler.start()

    dp.include_routers(
        user_commands.router,
        work_with_db.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
