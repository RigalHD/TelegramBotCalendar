import asyncio
import keyboards

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from cfgs import TOKEN

bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Приветствую, <b>{message.from_user.first_name}</b>", reply_markup=keyboards.main_keyboard)
    await message.answer(f"{message.from_user.id, message.from_user.id}")


@dp.message(Command(commands=["download", "скачать", "файл"]))
async def file_download(message: Message, command: CommandObject):
    pass


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
