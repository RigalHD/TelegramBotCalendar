import asyncio
import keyboards

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from cfgs import TOKEN

bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Приветствую, <b>{message.from_user.first_name}</b>", reply_markup=keyboards.main_keyboard)
    await message.answer(f"Ваш айди -> {message.from_user.id}")


@dp.message(Command(commands=["test_command"]))
async def command_test(message: Message, command: CommandObject):
    pass


@dp.message(F.text.lower() == "калькулятор")
async def calculator(message: Message):
    await message.answer(f"1 + 1 = 2")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    print("BOT IS READY TO WORK")

if __name__ == "__main__":
    asyncio.run(main())
