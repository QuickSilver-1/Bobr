from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery
from keyboards import *
from media import *
from config import config_1
from psycopg2 import connect
from psycopg2.errors import UniqueViolation


dp = Dispatcher()
bot = Bot(token=config_1.TOKEN)

class Delete(StatesGroup):
    delete_msg_id = State()

class Form(StatesGroup):
    await_msg = State()

class Register(StatesGroup):
    fio = State()
    email = State()
    number = State()
    username = State()
    password = State()

# @dp.message(F.photo)
# async def photo_handler(message: Message) -> None:
#     photo_data = message.photo[-1]

#     await message.answer(f'{photo_data}')

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
            print(mes)
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

@dp.callback_query(F.data == "Нету")
async def register(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Register.fio)
    await state.update_data(username=callback.message.from_user.username, tg_id=callback.message.from_user.id)
    await callback.message.answer(text="Вам нужно пройти небольшую регистрацию. Введите ФИО в формате 'Иванов Иван Иванович'")

@dp.message(Register.fio)
async def reg_fio(message: Message, state: FSMContext) -> None:
    try:
        last_name, first_name, second_name = message.text.split()
    except:
        await message.answer(text="Неправильный формат данных, попробуйте снова")
        return None
    await state.update_data(first_name=first_name, last_name=last_name, second_name=second_name, username_tg=message.from_user.username, tg_id=message.from_user.id)
    await state.set_state(Register.email)
    await message.answer(text="Введите свою почту")

@dp.message(Register.email)
async def reg_email(message: Message, state: FSMContext) -> None:
    if match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', message.text) is None:
        await message.answer(text="Неправильный формат данных, попробуйте снова")
    else:
        connection = connect(config_1.POSTGRES_URL)
        cursor = connection.cursor()
        cursor.execute(f'''SELECT COUNT(*) FROM "person" WHERE email = '{message.text}';''')
        if cursor.fetchone()[0] > 0:
            await message.answer(text="Пользователь с такой почтой уже есть", reply_markup=sign_in_kb())
        else:
            await state.update_data(email=message.text)
            await state.set_state(Register.number)
            await message.answer(text="Введите номер своего телефона")

@dp.message(Register.number)
async def reg_number(message: Message, state: FSMContext) -> None:
    if match("^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$", message.text) is None:
        await message.answer(text="Неправильный формат данных, попробуйте снова")
    else:
        await state.update_data(number=message.text)
        await state.set_state(Register.username)
        await message.answer(text="Придумайте себе имя пользователя\nОно должно состоять из символов латинского алфавита, цифр, а также символов: _ $ ^ #\nДлина от 3 до 15 символов")

@dp.message(Register.username)
async def reg_username(message: Message, state: FSMContext) -> None:
    if match("^[a-zA-Z0-9_$^#]+$", message.text) is None or len(message.text) < 3 or len(message.text) > 15:
        await message.answer(text="Неправильный формат данных, попробуйте снова")
    else:
        await state.update_data(username=message.text)
        await state.set_state(Register.password)
        await message.answer(text="Придумайте себе пароль\nОно должно состоять из символов латинского алфавита, цифр, а также символов: _ $ ^ #\nДлина от 3 до 30 символов")

@dp.message(Register.password)
async def reg_password(message: Message, state: FSMContext) -> None:
    if match("^[a-zA-Z0-9_$^#]+$", message.text) is None or len(message.text) < 3 or len(message.text) > 30:
        await message.answer(text="Неправильный формат данных, попробуйте снова")
    else:
        await state.update_data(password=message.text)
        await message.answer(text="Запомните пароль. Далнейший вход в систему будет осуществлять через него", reply_markup=password_kb())

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

############################################################33 ШАБЛОН ДЛЯ ДВУХ СЛАЙДОВ
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