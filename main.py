import asyncio
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from all_keyboards.inline_keyboards import main_menu_kb
from cfgs import TOKEN
from config import main_menu_image_path
from utils import database
import datetime as dt
from aiogram.types import Message, FSInputFile
from main_commands import (
    main_menu,
    states,
    user_commands,
    db_creating_commands,
    booksview,
)


bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())


async def send_msg(bot: Bot):
    await bot.send_message(4153686151, "OK!")


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer_photo(
        photo=FSInputFile(main_menu_image_path),
        caption="Главное меню",
        reply_markup=main_menu_kb(message.from_user.id)
        )


async def send_reminder(info_message: str, group_id: int):
    await bot.send_message(chat_id=group_id, text=info_message)


async def sender_of_reminds(bot: Bot):
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
        all_data = cursor.execute("SELECT * FROM schedule WHERE expired = 0").fetchall()
        for data in all_data:
            group_id = data[-2]
            day, month, year = data[2].replace(",", ".").split(".")
            hour, minute = data[3].split(":")[:-1]
            meeting = database.SchedulerDatabase(
                data[0],
                datetime(
                    year=int(year),
                    month=int(month), 
                    day=int(day), 
                    hour=int(hour), 
                    minute=int(minute)
                )
            )
            if not meeting.is_expired():
                # data = list(data)
                # data[2], data[3] = data[3], data[2]
                data = list(data)
                data[3] = data[3][:3]
                database.SchedulerDatabase.add_job(
                    data=data[1:], 
                    id=data[0],
                    reminder_function=send_reminder
                )
                # info_message = f"""Внимание! Напоминаем о встрече книжного клуба!
                # Что на ней будет? - <b>{data[1]}</b>
                # Когда она будет? - <b>{data[2]}</b>
                # Во сколько приходить? - <b>{hour}:{minute}</b> """
                
                # date = datetime.strptime(f'{year}-{month}-{day}', "%Y-%m-%d") + dt.timedelta(days=1)
                # scheduler.add_job(
                #     send_reminder,
                #     'cron',
                #     hour=12,
                #     minute=00,
                #     day_of_week="sat",
                #     start_date=datetime.now(),
                #     end_date=date,
                #     kwargs={
                #         "info_message": info_message,
                #         "group_id": group_id
                #     },
                #     id="scheduler_job_" + str(data[0])
                # )
            


async def main():
    dp.include_routers(
        user_commands.router,
        states.router,
        db_creating_commands.router,
        main_menu.router,
        booksview.router,
    )
    await sender_of_reminds(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
