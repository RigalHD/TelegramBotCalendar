import asyncio
import all_keyboards.keyboards as keyboards

from aiogram import Router, F
from aiogram.types import Message


router = Router()


@router.message(F.text.lower() == "регистрация")
async def registration(message: Message):
    if message.chat.type == 'private':
        await message.answer(f"""Гайд на регистрацию тут
                            https://www.youtube.com/watch?v=dQw4w9WgXcQ""")

# Все это пока просто плейсхолдеры

@router.message(F.text.lower() == "расписание")
async def schedule(message: Message):
    await message.answer(f"Тихий час по расписанию")


@router.message(F.text.lower() == "о нас" )
async def about_us(message: Message):
    await message.answer(f"Не лезь не в свое дело")
    
