import asyncio
import aiohttp
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ===== ТВОЙ ТОКЕН =====
TOKEN = "8418191088:AAGsJ1BXtn3O5lQ2BFHz77steJJTBKH74D0"

# ===== whitelist =====
ALLOWED_USERS = [
    702815281   # ← ВСТАВЬ СВОЙ TELEGRAM ID
]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== PORT BINDING (ВАЖНО ДЛЯ RENDER) =====
PORT = int(os.environ.get("PORT", 10000))

# ===== Research engine =====
async def research_engine(query):
    sources = [
        "https://github.com/",
        "https://reddit.com/user/",
        "https://t.me/"
    ]

    signals = []

    async with aiohttp.ClientSession() as session:
        tasks = []

        for source in sources:
            url = source + query

            async def worker(link):
                try:
                    async with session.get(link, timeout=5) as resp:
                        if resp.status == 200:
                            return link
                except:
                    return None

            tasks.append(worker(url))

        results = await asyncio.gather(*tasks)

        signals = [r for r in results if r]

    confidence = min(len(signals) * 0.35, 1.0)

    return signals, confidence

# ===== Telegram Commands =====
@dp.message(Command("start"))
async def start(message: types.Message):

    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("⛔ Closed research bot")
        return

    await message.answer("""
🤖 Research OSINT Bot

Commands:
/scan username
""")

@dp.message(Command("scan"))
async def scan(message: types.Message):

    if message.from_user.id not in ALLOWED_USERS:
        return

    try:
        query = message.text.split()[1]

        await message.answer("🧠 Analysis running...")

        signals, confidence = await research_engine(query)

        if signals:
            await message.answer(
                "✅ Public signals:\n" +
                "\n".join(signals) +
                f"\nConfidence: {confidence:.2f}"
            )
        else:
            await message.answer("❌ Nothing found")

    except:
        await message.answer("Usage: /scan username")

# ===== MAIN LOOP =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
