import asyncio
import keyboards

from aiogram import Bot, F, Dispatcher
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from cfgs import TOKEN
from main_commands import user_commands


bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Приветствую, <b>{message.from_user.first_name}</b>",
        reply_markup=keyboards.main_keyboard)
    await message.answer(f"Ваш айди -> {message.from_user.id}")



async def main():
    dp.include_routers(
        user_commands.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    print("BOT IS READY TO WORK")


if __name__ == "__main__":
    asyncio.run(main())
