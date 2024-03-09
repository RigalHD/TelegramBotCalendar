from aiogram.filters import Command, CommandObject
from aiogram import Bot, Router, F
from aiogram.types import Message


router = Router()

@router.message(Command("db_test"))
async def command_test(message: Message, command: CommandObject):
    print(command.args)