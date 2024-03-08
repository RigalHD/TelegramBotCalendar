import asyncio
import keyboards

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
# from aiogram.types.user import User


bot = Bot("6165125073:AAE5hndOrmTNamhAOV6_aNn10aklMveTQFE", parse_mode="HTML")
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Приветствую, <b>{message.from_user.first_name}</b>", reply_markup=keyboards.main_keyboard)
    await message.answer(f"{message.from_user.id, message.from_user.id}")
    
# @dp.message(Command(commands=["VK"]))
# async def process_start_command(message: Message):
#     await message.reply('<a href="https://vk.com/meljnichenko">VK</a>',parse_mode="HTML")

@dp.message(Command(commands=["download", "скачать", "файл"]))
async def file_download(message: Message, command: CommandObject):
    pass

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())