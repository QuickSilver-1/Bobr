from logging import basicConfig, INFO
from asyncio import run
from bot import bot, dp


async def main():
    await dp.start_polling(bot)
    

if __name__ =="__main__":
    basicConfig(level=INFO)
    run(main())
