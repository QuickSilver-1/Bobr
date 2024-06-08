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
async def start_conversation(message: Message):
    if message.from_user.id in admins:
        pass
    else:
        await message.answer_photo(
            photo=hello_photo,
            caption=hello1_text,
            reply_markup=inline_kb_builder('hello1_text')
        )

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
