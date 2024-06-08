from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards import *
from media import *
from config import config_1


dp = Dispatcher()
bot = Bot(token=config_1.TOKEN)

class Delete(StatesGroup):
    delete_msg_id = State()

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

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    
    if message.from_user.id in admins:
        pass

    else:
        delete_id = await message.answer_photo(photo=hello_photo, caption=hello1_text, reply_markup=skip_page("hello"))
        await state.set_state(Delete.delete_msg_id)
        await state.update_data(msg_id=delete_id.message_id)

@dp.callback_query(F.data == "hello")
async def hello2(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=data.get("msg_id"))
    await callback.message.answer_photo(photo=hello_photo, caption=hello1_text, reply_markup=next_page("story_first1"))

@dp.callback_query(F.data == "story_first1")
async def hello2(callback: CallbackQuery, state: FSMContext):

    delete_id = await callback.message.answer_photo(photo=egypt_photo, caption=egypt1_text, reply_markup=skip_page("story_first2"))
    await state.set_state(Delete.delete_msg_id)
    await state.update_data(msg_id=delete_id.message_id)

@dp.callback_query(F.data == "story_first2")
async def hello2(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=data.get("msg_id"))
    await callback.message.answer_photo(photo=egypt_photo, caption=egypt2_text, reply_markup=next_page("story_first1"))


# @dp.callback_query(F.data == "Обо мне")
# async def get_message_about(callback: CallbackQuery):
#     await callback.message.answer_photo(photo=about_photo, caption=about_text, reply_markup=lesson_kb())

