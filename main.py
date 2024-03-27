import asyncio
import all_keyboards.keyboards as keyboards

from aiogram import Bot, F, Dispatcher
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from cfgs import TOKEN
from main_commands import user_commands, work_with_db


from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta


async def sendd():
    print("!")


async def timer():
    print(datetime.now())


async def send_msg(bot: Bot):
    await bot.send_message(997987348, "OK!")


bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
scheduler.add_job(lambda: send_msg(bot=Bot), 
                    trigger='cron', 
                    hour=datetime.now().hour, 
                    minute=datetime.now().minute + 1, 
                    start_date=datetime.now()) 
scheduler.start()
print("?")
# scheduler = BackgroundScheduler(timezone='Europe/Moscow')
# scheduler.add_job(sendd, 'interval', seconds=5)
# scheduler.start()
def tick():
    print('Tick! The time is: %s' % datetime.now())


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Приветствую, <b>{message.from_user.first_name}</b>",
        reply_markup=keyboards.main_keyboard)
    await message.answer(f"Ваш айди -> {message.from_user.id}")


async def main():
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(tick, 'interval', seconds=3)
    scheduler.add_job(send_msg, 'cron', second=datetime.now().second + 1, start_date=datetime.now(), kwargs={"bot": bot})
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
