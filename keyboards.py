from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from datetime import datetime
from media import *
from aiogram.types import WebAppInfo
from psycopg2 import connect

def skip_page(page):
    builder = InlineKeyboardBuilder()

    builder.button(
        text=">>>", callback_data=page
    )

    builder.adjust(1)
    return builder.as_markup()

def next_page(page):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Дальше", callback_data=page
    )

    builder.adjust(1)
    return builder.as_markup()
