import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from all_keyboards.inline_keyboards import main_menu_kb
from cfgs import TOKEN
from config import main_menu_image_path
from utils import database
from aiogram.types import Message, FSInputFile
from main_commands import (
    main_menu,
    states,
    db_creating_commands,
    booksview,
)


bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer_photo(
        photo=FSInputFile(main_menu_image_path),
        caption="Главное меню",
        reply_markup=main_menu_kb(message.from_user.id)
        )


async def send_reminder(info_message: str, group_id: int):
    await bot.send_message(chat_id=group_id, text=info_message)


async def sender_of_reminds():
    all_data = database.SchedulerDatabase.get_schedule()
    for data in all_data:
        database.SchedulerDatabase.add_job(
            data=data[1:], 
            id=data[0],
            reminder_function=send_reminder
        )


async def main():
    dp.include_routers(
        states.router,
        db_creating_commands.router,
        main_menu.router,
        booksview.router,
    )
    await sender_of_reminds()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
