import asyncio
import all_keyboards.keyboards as keyboards

from aiogram import Bot, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

router = Router()
from main import bot

@router.message(F.text.lower() == "регистрация")
async def command_test(message: Message):
    await message.answer(f"""гайд на регистрацию тут
                         https://www.youtube.com/watch?v=CBJiJcgmDmM&list=PLEYdORdflM3lkbY2N9mH8pfH_-wPR9q9R&index=2""")


@router.message(F.text.lower() == "расписание")
async def calculator(message: Message):
    await message.answer(f"Тихий час по расписанию")


@router.message(F.text.lower() == "о нас")
async def calculator(message: Message):
    await message.answer(f"Не лезь не в своё дело")
