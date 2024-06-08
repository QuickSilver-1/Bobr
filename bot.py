from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import InlineKeyboardButton
from aiogram.types import Message, CallbackQuery
from keyboards import *
from media import *
from config import config_1
from psycopg2 import connect
from psycopg2.errors import UniqueViolation
from re import match


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

@dp.message(F.photo)
async def photo_handler(message: Message) -> None:
    photo_data = message.photo[-1]

    await message.answer(f'{photo_data}')

# @dp.message(F.video)
# async def photo_handler(message: Message) -> None:
#     photo_data = message.video

#     await message.answer(f'{photo_data}')

# @dp.message(F.document)
# async def photo_handler(message: Message) -> None:
#     photo_data = message.document

#     await message.answer(f'{photo_data}')

# @dp.message(F.voice)
# async def photo_handler(message: Message) -> None:
#     photo_data = message.voice.file_id

#     await message.answer(f'{photo_data}')


admins = ["1051818216"]


async def create_user(tg_id, first_name, last_name):
    try:
        connection = connect(config_1.POSTGRES_URL)
        cursor = connection.cursor()
        cursor.execute(f'''INSERT INTO users (tg_id, first_name, last_name) VALUES ('{tg_id}', '{first_name}', '{last_name}')''')
        connection.commit()
        connection.close()
    except UniqueViolation:
        pass

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute('''SELECT tg_id FROM "admin"''')
    admins = cursor.fetchall()
    connection.close()
    if str(message.from_user.id) in [i[0] for i in admins]:
        await message.answer(admin_text, reply_markup=admin_kb())
    else:
        await user_start(message=message, state=state)
        
@dp.callback_query(F.data == "Попробовать функции пользователя")
async def admin_to_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Чтобы вернуться к админ-меню нажмите на кнопку снизу", reply_markup=back_reply_kb())
    await user_start(message=callback.message, state=state)

async def user_start(message, state: FSMContext):
    tg_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    await create_user(tg_id, first_name, last_name)
    delete_id = await message.answer_photo(photo=hello_photo, caption=hello1_text, reply_markup=inline_kb_builder('hello1_text'))
    await state.set_state(Delete.delete_msg_id)
    await state.update_data(msg_id=delete_id.message_id)
        
@dp.callback_query(F.data == "Настроить рассылку")
async def get_message(callback: CallbackQuery, state: FSMContext):
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
    data = await state.get_data()
    await callback.message.answer("Сообщение не отправлено", reply_markup=admin_kb())
    await state.clear()
    await bot.delete_message(chat_id=callback.message.chat.id, message_id = data.get("delete_msg"))

@dp.callback_query(F.data == "Получить рекомендации")
async def register(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Register.fio)
    await state.update_data(username=callback.message.from_user.username, tg_id=callback.message.from_user.id)
    await callback.message.answer(text="Расскажите немного о себе. Введите своё ФИО")

@dp.message(Register.fio)
async def reg_fio(message: Message, state: FSMContext) -> None:
    try:
        last_name, first_name, second_name = message.text.split()
    except:
        await message.answer(text="Неправильный формат данных, попробуйте снова")
        return None
    await state.update_data(first_name=first_name, last_name=last_name, second_name=second_name, username_tg=message.from_user.username, tg_id=message.from_user.id)
    await state.set_state(Register.age)
    await message.answer(text="Введите свой возраст")

@dp.message(Register.age)
async def reg_age(message: Message, state: FSMContext) -> None:
    await state.update_data(age=message.text)
    await message.answer(text="У вас чувствительные зубы?", reply_markup=teeth_kb())

@dp.callback_query(F.data == "Чувствительные")
async def reg_teeth(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(teeth=True)
    await callback.message.answer(text="У вас есть проблемы с деснами?", reply_markup=desna_kb())

@dp.callback_query(F.data == "Обычные")
async def reg_teeth(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(teeth=False)
    await callback.message.answer(text="У вас есть проблемы с деснами?", reply_markup=desna_kb())

@dp.callback_query(F.data == "Проблемные")
async def reg_teeth(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get("teeth"):
        await callback.message.answer_photo(caption=recomend_text, photo=black_medium_photo)

@dp.callback_query(F.data == "Хорошие")
async def reg_teeth(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(desna="нет")
    

@dp.message(F.text == "Вернуться")
async def back_to_admin(message: Message):
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute('''SELECT tg_id FROM "admin"''')
    admins = cursor.fetchall()
    connection.close()
    if str(message.from_user.id) in [i[0] for i in admins]:
        await message.answer(admin_text, reply_markup=admin_kb())

@dp.callback_query(F.data == "Запомнил")
async def reg_final(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    username_tg = data.get("username_tg")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    second_name = data.get("second_name")
    email  = data.get("email")
    tg_id = data.get("tg_id")
    number = data.get("number")
    username = data.get("username")
    password = data.get("password")
    password = config_1.crypt.encrypt(password)
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute(f'''INSERT INTO "person" (username_tg, first_name, last_name, second_name, email, number, tg_id, username, password)
                   VALUES ('{username_tg}', '{first_name}', '{last_name}', '{second_name}', '{email}', '{number}', '{tg_id}', '{username}', '{password.decode()}');''')
    connection.commit()
    await callback.message.answer(text="Регистрация успешно выполнена")
    await state.clear()
    await cmd_start(message=callback.message, reg=True)

@dp.callback_query(F.data == 'hello1_text')
async def process_stage_one(callback: CallbackQuery):
    await callback.message.edit_caption(
        caption=hello2_text,
        reply_markup=inline_kb_builder(
            'hello2_text'
        )
    )

@dp.callback_query(F.data == 'hello2_text')
async def process_stage_two(callback: Message):
    await callback.answer('')

    await callback.message.answer_photo(
            photo=egypt_photo,
            caption=egypt1_text,
            reply_markup=inline_kb_builder('egypt1_text')
        )
    
@dp.callback_query(F.data == 'egypt1_text')
async def process_stage_three(callback: CallbackQuery):
    await callback.message.edit_caption(
        caption=egypt2_text,
        reply_markup=inline_kb_builder(
                'egypt2_text'
        )
    )

# химикаты
@dp.callback_query(F.data == 'egypt2_text')
async def process_stage_four(callback: CallbackQuery):
    await callback.answer('')

    await callback.message.answer_photo(
        photo=chemicals_photo,
        caption=chemicals1_text,
        reply_markup=inline_kb_builder('chemicals1_text')
    )

@dp.callback_query(F.data == 'chemicals1_text')
async def process_stage_five(callback: CallbackQuery):
    await callback.message.edit_caption(
        caption=chemicals2_text,
        reply_markup=inline_kb_builder('chemicals2_text')
    )

# новая паста с добавлением пьезоэлектриков
@dp.callback_query(F.data == 'chemicals2_text')
async def process_stage_four(callback: CallbackQuery):
    await callback.answer('')

    await callback.message.answer_photo(
        photo=piezoelectricity_photo,
        caption=piezo_electricity1_text,
        reply_markup=inline_kb_builder('piezo_electricity1_text')
    )

@dp.callback_query(F.data == 'piezo_electricity1_text')
async def process_stage_five(callback: CallbackQuery):
    await callback.message.edit_caption(
        caption=piezo_electricity2_text,
        reply_markup=inline_kb_builder('piezo_electricity2_text')
    )


@dp.callback_query(F.data == 'piezo_electricity2_text')
async def process_stage_four(callback: CallbackQuery):
    await callback.answer('')

    await callback.message.answer_photo(
        photo=community_photo,
        caption=community1_text,
        reply_markup=inline_kb_builder('community1_text')
    )

@dp.callback_query(F.data == 'community1_text')
async def process_stage_five(callback: CallbackQuery):
    await callback.message.edit_caption(
        caption=community2_text,
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
    await callback.message.answer(
        text=decline_quiz_text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Группа ТГ', url='tg://biomed_global')
            ]
        ])
    )

# начало квиза
@dp.callback_query(F.data == 'START_QUIZ_ACTION', StateFilter(default_state))
async def process_start_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=first_question,
        reply_markup=quiz_question_keyboard(first_question)
    )

    await state.set_state(Quiz.name)
    await state.update_data(name=callback.from_user.first_name)
    await state.set_state(Quiz.first_question)

@dp.callback_query(StateFilter(Quiz.first_question))
async def process_second_question(callback: CallbackQuery, state: FSMContext):
    await state.update_data(first_question=F.data)
    await state.set_state(Quiz.second_question)

    await callback.message.edit_text(
        text=second_question,
        reply_markup=quiz_question_keyboard(second_question)
    )

@dp.callback_query(StateFilter(Quiz.second_question))
async def process_second_question(callback: CallbackQuery, state: FSMContext):
    await state.update_data(second_question=F.data)
    await state.set_state(Quiz.second_question)

    await callback.message.edit_text(
        text=third_question,
        reply_markup=quiz_question_keyboard(third_question)
    )

@dp.callback_query(StateFilter(Quiz.third_question))
async def process_second_question(callback: CallbackQuery, state: FSMContext):
    await state.update_data(third_question=F.data)
    await state.set_state(Quiz.fourth_question)

    await callback.message.edit_text(
        text=third_question,
        reply_markup=quiz_question_keyboard(fourth_question)
    )

@dp.callback_query(StateFilter(Quiz.fourth_question))
async def process_second_question(callback: CallbackQuery, state: FSMContext):
    await state.update_data(fifth_question=F.data)
    data = await state.get_data()

    if ((str(data['first_question']) == '60') + (data['second_question'] == 'Хелфи') + (str(data['third_question']) == '5') +\
          (data['fourth_question'] == 'применения пьезоэлектриков') + (str(data['fifth_question']) == '0')) >= 3:
        await callback.message.answer_photo(
            photo=winner_photo,
            caption=quiz_winner_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Группа ТГ', url='tg://biomed_global')
            ]
        ])
        )
    
    else:
        await callback.message.answer(
            text=failed_quiz,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Группа ТГ', url='tg://biomed_global')
            ]
        ])
        )

    # await callback.message.edit_text(
    #     text=third_question,
    #     reply_markup=quiz_question_keyboard(third_question)
    # )

############################################################ ШАБЛОН ДЛЯ ДВУХ СЛАЙДОВ
# @dp.callback_query(F.data == '')
# async def process_stage_four(callback: CallbackQuery):
#     await callback.answer('')

#     await callback.message.answer_photo(
#         photo=chemicals_photo,
#         caption=,
#         reply_markup=inline_kb_builder('')
#     )

# @dp.callback_query(F.data == '')
# async def process_stage_five(callback: CallbackQuery):
#     await callback.message.edit_caption(
#         caption=,
#         reply_markup=inline_kb_builder('')
#     )