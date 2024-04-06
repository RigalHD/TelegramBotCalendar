import asyncio
import all_keyboards.keyboards as keyboards

from aiogram import Bot, Router, F
from aiogram.types import Message

router = Router()


@router.message(F.text.lower() == "регистрация")
async def command_test(message: Message):
    await message.answer(f"""Гайд на регистрацию тут
                         https://www.youtube.com/watch?v=dQw4w9WgXcQ""")


@router.message(F.text.lower() == "расписание")
async def calculator(message: Message):
    await message.answer(f"Тихий час по расписанию")


@router.message(F.text.lower() == "о нас")
async def calculator(message: Message):
    await message.answer(f"Не лезь не в своё дело")
