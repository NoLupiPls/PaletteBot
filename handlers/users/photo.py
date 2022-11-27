import os
import sqlite3

import colorgram
from PIL import Image
from aiogram import types
from aiogram.dispatcher import FSMContext
from io import BytesIO

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp, bot, _
# from data.config import OWNER as own


def clrs(colors):
    return [('#%02x%02x%02x' % (color.rgb.r, color.rgb.g, color.rgb.b)).upper() for color in colors]


def image_to_byte_array(image: Image):
    imgByteArr = BytesIO()
    image.save(imgByteArr, format='PNG')
    return imgByteArr.getvalue()


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def process_photo(message: types.Message, state: FSMContext):
    await bot.send_chat_action(message.chat.id, 'upload_photo')
    fileID = message.photo[-1].file_id
    file_info = await bot.get_file(fileID)

    downloaded_file = (await bot.download_file(file_info.file_path)).read()
    my_path = 'handlers//users//img//' + str(fileID) + '.jpg'
    with open(my_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    colors = clrs(colorgram.extract(my_path, 6))
    # os.remove(f"img/{fileID}.jpg")

    for color in colors:
        img = image_to_byte_array(Image.new('RGB', (320, 125), color))
        if colors[-1] == color:
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton(_('Сохранить палитру'), callback_data='save'))
            await message.answer_photo(img, caption=f'`{color}`', parse_mode='MARKDOWN', reply_markup=markup)
        else:
            await message.answer_photo(img, caption=f'`{color}`', parse_mode='MARKDOWN')

    async with state.proxy() as data:
        data['palette'] = colors


@dp.callback_query_handler(lambda c: c.data == 'save')
async def save_palette_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if 'palette' in data.keys():
            conn = sqlite3.connect("database/users.db")
            cursor = conn.cursor()
            cursor.execute('INSERT INTO palettes VALUES(?, ?)',
                           (callback_query.message.chat.id, ', '.join(data['palette'])))
            conn.commit()
            conn.close()
            await callback_query.message.delete_reply_markup()
            await callback_query.message.answer(_('Сохранено!'))
        else:
            await bot.answer_callback_query(callback_query.id, _('Я извиняюсь, но я не могу сохранить её.'))
