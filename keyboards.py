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

def teeth_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Да", callback_data="Чувствительные"
    )
    builder.button(
        text="Нет", callback_data="Обычные"
    )
    builder.adjust(1)
    return builder.as_markup()

def desna_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Да", callback_data="Проблемные"
    )
    builder.button(
        text="Нет", callback_data="Хорошие"
    )
    builder.adjust(1)
    return builder.as_markup()

def back_reply_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(
        text="Вернуться",
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
            text=str(button_label),
            callback_data=str(button_label)
        )
    
    return builder.as_markup(resize_keyboard=True)