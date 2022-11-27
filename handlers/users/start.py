from aiogram import types

from loader import dp, _
# from data.config import OWNER as own


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    name = message.from_user.first_name
    hi = _(f"👋 Привет, {name}, отправь мне фотографию и я создам палитру на её основе!")
    await message.answer(hi)
