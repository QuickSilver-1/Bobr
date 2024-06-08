from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from datetime import datetime
from media import *
from aiogram.types import WebAppInfo
from psycopg2 import connect
from media import *



def admin_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Настроить рассылку", callback_data="Настроить рассылку"
    )
    builder.button(
        text="Попробовать функции пользователя", callback_data="Попробовать функции пользователя"
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

def reply_kb_builder(buttons: list) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for button in buttons:
        builder.button(
            text=button,
        )

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def inline_kb_builder(callback: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=callback_keys[callback],
        callback_data=callback
    )

    return builder.as_markup(resize_keyboard=True)

def quiz_question_keyboard(question_number: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for button_label in questions[question_number]:
        builder.button(
            text=button_label,
            callback_data=button_label
        )
    
    return builder.as_markup(resize_keyboard=True)