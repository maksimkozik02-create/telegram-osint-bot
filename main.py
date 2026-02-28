import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "8418191088:AAFEANI4tnCVeTKo6eMheSrc2C3OVnAdC7A"

ALLOWED_USERS = {702815281}

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):

    if message.from_user.id not in ALLOWED_USERS:
        return

    await message.answer("Bot working!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
