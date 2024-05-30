import asyncio
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from all_keyboards import keyboards
from all_keyboards.inline_keyboards import main_menu_kb
from cfgs import TOKEN
from config import main_menu_image_path
from utils import database
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


async def send_reminder(bot: Bot, info_message: str, group_id: int):
    await bot.send_message(chat_id=group_id, text=info_message)


async def sender_of_reminds(bot: Bot):
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
        all_data = cursor.execute("SELECT * FROM schedule WHERE expired = 0").fetchall()
        for i in range(len(all_data)):
            hour, minute = all_data[i][3].split(":")[:-1]
            group_id = all_data[i][-1]
            info_message = f"""Внимание! Напоминаем о встрече книжного клуба!
            Что на ней будет? - <b>{all_data[i][1]}</b>
            Когда она будет? - <b>{hour}:{minute}</b>
            Во сколько приходить? - <b>{all_data[i][2]}</b> """

            scheduler.add_job(
                send_reminder, 'cron',
                hour=12,
                minute=0, 
                start_date=datetime.now(),  # ЗАМЕНИТЬ НА НУЖНУЮ ДАТУ ПОТОМ!!!!!!!!!!!!!!!!!!!!!!
                kwargs={
                "bot": bot,
                "info_message": info_message,
                "group_id": group_id
                },
                id="main_job_" + str(i) 
                )
        
        return scheduler


async def main():
    dp.include_routers(
        user_commands.router,
        states.router,
        db_creating_commands.router,
        main_menu.router,
        booksview.router,
    )
    sch = await sender_of_reminds(bot)
    sch.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
