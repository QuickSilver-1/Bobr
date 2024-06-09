from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import InlineKeyboardButton, InputMediaPhoto
from aiogram.types import Message, CallbackQuery
from keyboards import *
from media import *
from config import config_1
from psycopg2 import connect
from psycopg2.errors import UniqueViolation
from asyncio import sleep
from random import choice
from hmac import new
from hashlib import sha256

dp = Dispatcher()
bot = Bot(token=config_1.TOKEN)

class Delete(StatesGroup):
    delete_msg_id = State()

class Form(StatesGroup):
    await_msg = State()

class Register(StatesGroup):
    fio = State()
    age = State()
    teeth = State()


async def create_user(tg_id, first_name, last_name, username):
    try:
        connection = connect(config_1.POSTGRES_URL)
        cursor = connection.cursor()
        cursor.execute(f'''INSERT INTO users (tg_id, first_name, last_name, username) VALUES ('{tg_id}', '{first_name}', '{last_name}', '{username}')''')
        connection.commit()
        connection.close()
    except UniqueViolation:
        pass

@dp.message(CommandStart())
async def cmd_start(message: Message):
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute('''SELECT tg_id FROM "admin"''')
    admins = cursor.fetchall()
    connection.close()
    if str(message.from_user.id) in [i[0] for i in admins]:
        await message.answer(admin_text, reply_markup=admin_kb())
    else:
        await user_start(message=message)

@dp.callback_query(F.data == "Попробовать функции пользователя")
async def admin_to_user(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")

    await callback.message.answer(text="Чтобы вернуться к админ-меню нажмите на кнопку снизу", reply_markup=back_reply_kb())
    await user_start(message=callback.message)

        
@dp.message(F.text == "Вернуться в админ-панель")
async def back_to_home(message: Message):
    await cmd_start(message)

async def user_start(message):
    tg_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    await create_user(tg_id, first_name, last_name, username)
    await message.answer_photo(photo=hello1_photo, caption=hello1_text.format(name=message.from_user.first_name), reply_markup=inline_kb_builder('hello1_text'))
        
@dp.callback_query(F.data == "Настроить рассылку")
async def get_message(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")

    await state.set_state(Form.await_msg)
    await callback.message.answer("Введите текст, который вы хотите разослать или добавьте медиа-файлы")

@dp.message(Form.await_msg)
async def send_msg(message: Message, state: FSMContext) -> None:
    await state.update_data(await_msg = message)

    sure = await message.answer(text = "Вы уверены, что хотите отправить это сообщение?", 
                                reply_markup = are_you_sure())
    await state.update_data(delete_msg = sure.message_id)

@dp.callback_query(F.data == "Да")
async def send_all(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("")

    data = await state.get_data()
    mes = data.get("await_msg")
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT tg_id FROM users")
        users = cursor.fetchall()
    except Exception as e:
        print(f"The error '{e}' occurred")
    
    if mes.photo == None:
        for user in users:
            await bot.send_message(chat_id=user[0], text=mes.text)
    else:
        for user in users:
            await bot.send_photo(chat_id=user[0], photo=mes.photo[-1].file_id, caption=mes.caption)

    await callback.message.answer("Сообщение отправлено пользователям", reply_markup=admin_kb())
    await state.clear()
    await bot.delete_message(chat_id=callback.message.chat.id, message_id = data.get("delete_msg"))

@dp.callback_query(F.data == "Нет")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")

    data = await state.get_data()
    await callback.message.answer("Сообщение не отправлено", reply_markup=admin_kb())
    await state.clear()
    await bot.delete_message(chat_id=callback.message.chat.id, message_id = data.get("delete_msg"))

@dp.callback_query(F.data == "Получить рекомендации")
async def register(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")

    await state.set_state(Register.fio)
    await state.update_data(username=callback.message.from_user.username, tg_id=callback.message.from_user.id)
    await callback.message.answer(text="Расскажите немного о себе. Введите своё имя")

@dp.message(Register.fio)
async def reg_fio(message: Message, state: FSMContext) -> None:

    await state.update_data(first_name=message.text, username_tg=message.from_user.username, tg_id=message.from_user.id)
    await state.set_state(Register.age)
    await message.answer(text="Введите свой возраст")

@dp.message(Register.age)
async def reg_age(message: Message, state: FSMContext) -> None:
    await state.update_data(age=message.text)
    await message.answer(text="У вас чувствительные зубы?", reply_markup=teeth_kb())

@dp.callback_query(F.data == "Чувствительные")
async def reg_teeth(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("")

    await state.update_data(teeth=True)
    await callback.message.answer(text="У вас есть проблемы с деснами?", reply_markup=desna_kb())

@dp.callback_query(F.data == "Обычные")
async def reg_teeth(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("")

    await state.update_data(teeth=False)
    await callback.message.answer(text="У вас есть проблемы с деснами?", reply_markup=desna_kb())

@dp.callback_query(F.data == "Проблемные")
async def reg_teeth(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("")

    data = await state.get_data()
    if data.get("teeth"):
        await callback.message.answer(text=recomend_text)
        await sleep(1)
        await callback.message.answer_photo(photo=black_medium_photo, caption=black_medium_text)
        await sleep(1)
        await callback.message.answer_photo(photo=gum_health_photo, caption=gum_health_text)
        await sleep(1)
        await callback.message.answer_photo(photo=well_gum_photo, caption=well_gum_text)

    else:
        await callback.message.answer(text=recomend_text)
        await sleep(1)
        await callback.message.answer_photo(photo=black_medium_photo, caption=black_medium_text)
        await sleep(1)
        await callback.message.answer_photo(photo=superwhite_photo, caption=superwhite_text)
        await sleep(1)
        await callback.message.answer_photo(photo=superwhiteop_photo, caption=superwhiteop_text)

    await reg_final(callback=callback, state=state)

@dp.callback_query(F.data == "Хорошие")
async def reg_teeth(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("")

    data = await state.get_data()
    if data.get("teeth"):
        await callback.message.answer(text=recomend_text)
        await sleep(1)
        await callback.message.answer_photo(photo=silver_medium_photo, caption=silver_medium_text)
        await sleep(1)
        await callback.message.answer_photo(photo=white_complex_photo, caption=white_complex_text)
        await sleep(1)
        await callback.message.answer_photo(photo=sensetive_photo, caption=sensetive_text)

    else:
        await callback.message.answer(text=recomend_text)
        await sleep(1)
        await callback.message.answer_photo(photo=mineral_hard_photo, caption=mineral_hard_text)
        await sleep(1)
        await callback.message.answer_photo(photo=calcimax_photo, caption=calcimax_text)
        await sleep(1)
        await callback.message.answer_photo(photo=vitafresh_photo, caption=vitafresh_text)

    await reg_final(callback=callback, state=state)
    
async def reg_final(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    age = data["age"]
    age = new(config_1.SECRET_KEY, str(age).encode(), sha256).hexdigest()
    tg_id = callback.from_user.id
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute(f'''UPDATE "users" SET age = '{age}' WHERE tg_id = '{tg_id}';''')
    connection.commit()
    await state.clear()
    await callback.message.answer(text=main_text, reply_markup=main_menu_kb())

@dp.callback_query(F.data == 'hello1_text')
async def process_stage_one(callback: CallbackQuery):
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=hello2_photo,
            caption=hello2_text,
        ),
        reply_markup=inline_kb_builder(
            'hello2_text'
        )
    )

@dp.callback_query(F.data == 'hello2_text')
async def process_stage_two(callback: Message):
    await callback.answer('')

    await callback.message.answer_photo(
            photo=egypt1_photo,
            caption=egypt1_text,
            reply_markup=inline_kb_builder('egypt1_text')
        )
    
@dp.callback_query(F.data == 'egypt1_text')
async def process_stage_three(callback: CallbackQuery):
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=egypt2_photo,
            caption=egypt2_text,
        ),
        reply_markup=inline_kb_builder(
                'egypt2_text'
        )
    )

# химикаты
@dp.callback_query(F.data == 'egypt2_text')
async def process_stage_four(callback: CallbackQuery):
    await callback.answer('')

    await callback.message.answer_photo(
        photo=chemicals1_photo,
        caption=chemicals1_text,
        reply_markup=inline_kb_builder('chemicals1_text')
    )

@dp.callback_query(F.data == 'chemicals1_text')
async def process_stage_five(callback: CallbackQuery):
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=chemicals2_photo,
            caption=chemicals2_text,
        ),
        reply_markup=inline_kb_builder('chemicals2_text')
    )

# новая паста с добавлением пьезоэлектриков
@dp.callback_query(F.data == 'chemicals2_text')
async def process_stage_four(callback: CallbackQuery):
    await callback.answer('')

    await callback.message.answer_photo(
        photo=piezoelectricity1_photo,
        caption=piezo_electricity1_text,
        reply_markup=inline_kb_builder('piezo_electricity1_text')
    )

@dp.callback_query(F.data == 'piezo_electricity1_text')
async def process_stage_five(callback: CallbackQuery):
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=piezoelectricity2_photo,
            caption=piezo_electricity2_text,
        ),
        reply_markup=inline_kb_builder('piezo_electricity2_text')
    )


@dp.callback_query(F.data == 'piezo_electricity2_text')
async def process_stage_four(callback: CallbackQuery):
    await callback.answer('')

    await callback.message.answer_photo(
        photo=community1_photo,
        caption=community1_text,
        reply_markup=inline_kb_builder('community1_text')
    )

@dp.callback_query(F.data == 'community1_text')
async def process_stage_five(callback: CallbackQuery):
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=community2_photo,
            caption=community2_text,
        ),
        reply_markup=inline_kb_builder('community2_text')
    )

class Quiz(StatesGroup):
    name = State()
    first_question = State()
    second_question = State()
    third_question = State()
    fourth_question = State()
    fifth_question = State()

@dp.callback_query(F.data == 'community2_text', StateFilter(default_state))
async def process_ask_to_start_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')

    await callback.message.answer_photo(
        photo=start_quiz_photo,
        caption=quiz_introduction_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Да, давай!',
                    callback_data='START_QUIZ_ACTION'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Извини, давай в другой раз(',
                    callback_data='DECLINE_QUIZ_ACTION'
                )
            ]
        ])
    )

# отмена квиза
@dp.callback_query(F.data == 'DECLINE_QUIZ_ACTION', StateFilter(default_state))
async def process_decline_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")

    await callback.message.answer(text=decline_quiz_text, reply_markup=main_kb())

# начало квиза
@dp.callback_query(F.data == 'START_QUIZ_ACTION', StateFilter(default_state))
async def process_start_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")

    delete_message = await callback.message.answer(
        text=first_question,
        reply_markup=quiz_question_keyboard('first_question')
    )

    await state.set_state(Quiz.name)
    await state.update_data(name=callback.from_user.first_name, delete_message=delete_message.message_id)
    await state.update_data(count=0)
    await state.set_state(Quiz.first_question)

@dp.callback_query(StateFilter(Quiz.first_question))
async def process_second_question(callback: CallbackQuery, state: FSMContext):
    if callback.data == '60':
        counter = await state.get_data()
        await state.update_data(count=counter['count'] + 1)
    await state.set_state(Quiz.second_question)

    await callback.message.edit_text(
        text=second_question,
        reply_markup=quiz_question_keyboard('second_question')
    )

@dp.callback_query(StateFilter(Quiz.second_question))
async def process_second_question(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'Хелфи':
        counter = await state.get_data()
        await state.update_data(count=counter['count'] + 1)
    await state.set_state(Quiz.third_question)

    await callback.message.edit_text(
        text=third_question,
        reply_markup=quiz_question_keyboard('third_question')
    )

@dp.callback_query(StateFilter(Quiz.third_question))
async def process_second_question(callback: CallbackQuery, state: FSMContext):
    if callback.data == '5':
        counter = await state.get_data()
        await state.update_data(count=counter['count'] + 1)
    await state.set_state(Quiz.fourth_question)

    await callback.message.edit_text(
        text=fourth_question,
        reply_markup=quiz_question_keyboard('fourth_question')
    )

@dp.callback_query(StateFilter(Quiz.fourth_question))
async def process_second_question(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'пьезоэлектриков':
        counter = await state.get_data()
        await state.update_data(count=counter['count'] + 1)
    await state.set_state(Quiz.fifth_question)

    await callback.message.edit_text(
        text=fifth_question,
        reply_markup=quiz_question_keyboard('fifth_question')
    )

@dp.callback_query(StateFilter(Quiz.fifth_question))
async def process_second_question(callback: CallbackQuery, state: FSMContext):
    if callback.data == '0':
        counter = await state.get_data()
        await state.update_data(count=counter['count'] + 1)
    data = await state.get_data()
    await state.clear()

    await bot.delete_message(chat_id=callback.message.chat.id, message_id=data['delete_message'])
    if data['count'] >= 3:

        await callback.message.answer_photo(
            photo=winner_photo,
            caption=quiz_winner_text,
            reply_markup=main_kb()
        )
    
    
    else:
        await callback.message.answer(text=failed_quiz, reply_markup=main_kb(loose=True))

@dp.callback_query(F.data == "Главное меню")
async def main_menu(callback: CallbackQuery):
    await callback.message.delete()

    # await callback.message.answer(text=main_text, reply_markup=main_menu_kb())

@dp.callback_query(F.data == "Маркетплейсы")
async def marketplays(callback: CallbackQuery):
    await callback.answer("")

    await callback.message.answer(text=market_text, reply_markup=market_kb())

@dp.callback_query(F.data == "Розыгрыш")
async def fortune(callback: CallbackQuery):
    await callback.message.answer_photo(photo=fortune_photo, caption=fortune_text, reply_markup=main_kb())
    
@dp.callback_query(F.data == "Рандом")
async def random_admin(callback: CallbackQuery, state: FSMContext):
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute('''SELECT tg_id, username FROM "users";''')
    username = choice(cursor.fetchall())
    msg = await callback.message.answer(text=random_text.format(username=username[1]), reply_markup=random_kb())
    await state.set_state(Delete.delete_msg_id)
    await state.update_data(msg_id=msg.message_id, winner_id=username[0], username=username[1])

@dp.callback_query(F.data == "Выбрать другого")
async def fortune(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=data["msg_id"])
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute('''SELECT tg_id, username FROM "users";''')
    username = choice(cursor.fetchall())
    msg = await callback.message.answer(text=random_text.format(username=username[1]), reply_markup=random_kb())
    await state.set_state(Delete.delete_msg_id)
    await state.update_data(msg_id=msg.message_id, winner_id=username[0], username=username[1])
    
@dp.callback_query(F.data == "Победитель")
async def fortune(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=data["msg_id"])
    await callback.message.answer(text=f'Сообщение отправлено победителю @{data["username"]}', reply_markup=admin_kb())
    await bot.send_photo(chat_id=data["winner_id"], photo=winner_photo, caption=winner_text)
    await state.clear()