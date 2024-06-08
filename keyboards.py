from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from datetime import datetime
from media import *
from aiogram.types import WebAppInfo
from psycopg2 import connect


def admin_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Настроить рассылку", callback_data="Настроить рассылку"
    )

    builder.adjust(1)
    return builder.as_markup()

def are_you_sure():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Да", callback_data="Да"
    )
    builder.button(
        text="Нет", callback_data="Нет"
    )
    builder.adjust(1)
    return builder.as_markup()

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
