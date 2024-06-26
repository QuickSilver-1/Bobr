from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from media import *


def admin_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Настроить рассылку", callback_data="Настроить рассылку"
    )
    builder.button(
        text="Попробовать функции пользователя", callback_data="Попробовать функции пользователя"
    )
    builder.button(
        text="Розыгрыш", callback_data="Рандом"
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
        text="Вернуться в админ-панель",
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

    if question_number == 'fourth_question':
        builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)

def main_kb(loose=False):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Главное меню", callback_data="Главное меню"
    )

    if loose:
        builder.button(
            text='Попробовать ещё раз', callback_data='START_QUIZ_ACTION'
        )

    builder.adjust(1)
    return builder.as_markup()

def main_menu_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Какая паста нужнам именно мне?", callback_data="Получить рекомендации"
    )
    builder.button(
        text="А что тут?", url="https://t.me/biomed_global"
    )
    builder.button(
        text="Всё для белоснежной улыбки", callback_data="Маркетплейсы"
    )
    builder.button(
        text="Еженедельный розыгрыш призов!", callback_data="Розыгрыш"
    )

    builder.adjust(1)
    return builder.as_markup()


def market_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Ozon", url="https://www.ozon.ru/brand/biomed-18821767/"
    )
    builder.button(
        text="Wildberries", url="https://www.wildberries.ru/brands/7757-biomed"
    )
    builder.button(
        text="Вернуться в главное меню", callback_data="Главное меню"
    )

    builder.adjust(1)
    return builder.as_markup()

def random_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Отправить уведомление пользвателю", callback_data="Победитель"
    )
    builder.button(
        text="Выбрать другого", callback_data="Выбрать другого"
    )

    builder.adjust(1)
    return builder.as_markup()