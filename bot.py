from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards import *
from media import *
from config import config_1
from asyncpg import UniqueViolationError
from psycopg2 import connect


dp = Dispatcher()
bot = Bot(token=config_1.TOKEN)

class Delete(StatesGroup):
    delete_msg_id = State()

class Form(StatesGroup):
    await_msg = State()

@dp.message(F.photo)
async def photo_handler(message: Message) -> None:
    photo_data = message.photo[-1]

    await message.answer(f'{photo_data}')

@dp.message(F.video)
async def photo_handler(message: Message) -> None:
    photo_data = message.video

    await message.answer(f'{photo_data}')

@dp.message(F.document)
async def photo_handler(message: Message) -> None:
    photo_data = message.document

    await message.answer(f'{photo_data}')

@dp.message(F.voice)
async def photo_handler(message: Message) -> None:
    photo_data = message.voice.file_id

    await message.answer(f'{photo_data}')


admins = ["1051818216"]


async def create_user(tg_id, first_name, last_name):
    try:
        connection = connect(config_1.POSTGRES_URL)
        cursor = connection.cursor()
        cursor.execute(f'''INSERT INTO users (tg_id, first_name, last_name) VALUES ('{tg_id}', '{first_name}', '{last_name}')''')
        connection.commit()
        connection.close()
    except UniqueViolationError:
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
        delete_id = await message.answer_photo(photo=hello_photo, caption=hello1_text, reply_markup=inline_kb_builder(F.data == 'hello1_text'))
        await state.set_state(Delete.delete_msg_id)
        await state.update_data(msg_id=delete_id.message_id)
        
@dp.callback_query(F.data == "Настроить рассылку")
async def get_message(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.await_msg)
    await callback.message.answer("Введите текст, который вы хотите разослать или добавьте фотографию")
    dp.message.register(send_msg)

@dp.message(Form.await_msg)
async def send_msg(message: Message, state: FSMContext) -> None:
    await state.update_data(await_msg = message.text)
    await state.set_state(Form.await_msg)
    sure = await message.answer(text = "Вы уверены, что хотите отправить это сообщение?", 
                                reply_markup = are_you_sure())
    global mail, chat, mes
    chat = message.chat.id
    mes = sure.message_id
    try:
        mail = [message.caption, f"{message.photo[-1].file_id}"]
    except:
        mail = message.text

@dp.callback_query(F.data == "Да")
async def send_all(callback: CallbackQuery) -> None:
    connection = connect(
            database=config_1.DATABASE,
            user=config_1.PGUSER,
            password=config_1.PGPASSWORD,
            host=config_1.ip,
            port=5432)
    select_users = "SELECT tg_id FROM users"
    cursor = connection.cursor()
    try:
        cursor.execute(select_users)
        users = cursor.fetchall()
    except Exception as e:
        print(f"The error '{e}' occurred")
    for user in users:
        if type(mail) == list:
            await bot.send_photo(chat_id = str(user[0]), 
                                 photo = mail[1], 
                                 caption = mail[0])
        else:
            await bot.send_message(str(user[0]), 
                                   mail)
    await callback.message.answer("Сообщение отправлено пользователям")
    await bot.delete_message(chat_id = chat, 
                             message_id = mes)

@dp.callback_query(F.data == "Нет")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Сообщение не отправлено")
    await state.clear()
    await bot.delete_message(chat_id = chat, 
                             message_id = mes)








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
