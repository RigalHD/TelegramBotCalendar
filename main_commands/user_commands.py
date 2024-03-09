import asyncio
import keyboards

from aiogram import Bot, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

router = Router()
from main import bot

@router.message(F.text.lower() == "test_bot")
async def command_test(message: Message):
    print("ok")


@router.message(F.text.lower() == "калькулятор")
async def calculator(message: Message):
    await message.answer(f"1 + 1 = 2")
#Я гей