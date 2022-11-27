import sqlite3

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from loader import dp, _
# from data.config import OWNER as own


@dp.message_handler(commands=['palettes'])
async def send_palettes(message: types.Message, state: FSMContext):
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM palettes WHERE cid = {message.chat.id}')
    palettes = cursor.fetchall()
    if len(palettes) == 0:
        await message.answer(_('У тебя ещё не сохранено ни одной палитры.'))
    elif len(palettes) == 1:
        markup = color_markup(palettes[0][1].split(', '))
        await message.answer(_('Твоя палитра'), reply_markup=markup)
    else:
        palettes = [p[1].split(', ') for p in palettes]
        async with state.proxy() as data:
            data['palettes'] = palettes
            data['palindex'] = 0
        markup = color_markup(palettes[0])
        markup.add(InlineKeyboardButton('▶', callback_data='next'))
        await message.answer(_('Твои палитры'), reply_markup=markup)


def color_markup(colors):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    return rec_markup([InlineKeyboardButton(color, callback_data=color) for color in colors], markup)


def rec_markup(buttons, markup):
    if len(buttons) <= 3:
        markup.row(*buttons)
        return markup
    else:
        a, b, c = buttons[-1], buttons[-2], buttons[-3]
        markup.row(a, b, c)
        return rec_markup(buttons[:-3], markup)
