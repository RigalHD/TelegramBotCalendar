from aiogram.filters import Command, CommandObject
from aiogram import Router
from aiogram.types import Message, FSInputFile
from all_keyboards import inline_keyboards
from config import all_books_image_path

router = Router()


@router.message(Command("view_random_books"))
async def view_random_books(message: Message, command: CommandObject):
    if message.from_user.id != 997987348:
        await message.answer(text="Отказано в доступе")
        return
    await message.answer_photo(
    photo=FSInputFile(all_books_image_path),
    caption=f"Мы рекомендуем вам эти книги",
    reply_markup=inline_keyboards.all_books_kb())


@router.message(Command("vote_for_books"))
async def vote_for_books(message: Message, command: CommandObject):
    # ! временная заглушка
    if message.from_user.id != 997987348:
        await message.answer(text="Отказано в доступе")
        return
    await message.answer_photo(
    photo=FSInputFile(all_books_image_path),
    caption=f"Мы рекомендуем вам эти книги",
    reply_markup=inline_keyboards.all_books_kb())
