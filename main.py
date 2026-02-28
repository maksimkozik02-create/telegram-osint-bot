import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# =============================
# CONFIGURATION
# =============================

TOKEN = "8418191088:AAEaLSjTJc7XqUBE341iK_jzzTFwkMsZ_Hs"

# Telegram ID whitelist
ALLOWED_USERS = [
    702815281
]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =============================
# PUBLIC RESEARCH SOURCES
# =============================

RESEARCH_SOURCES = [
    "https://github.com/",
    "https://reddit.com/user/",
    "https://t.me/"
]

# =============================
# ACCESS CONTROL
# =============================

def access(user_id: int):
    return user_id in ALLOWED_USERS

# =============================
# INTELLIGENCE RESEARCH ENGINE
# =============================

async def research_engine(query: str):

    signals = []

    async with aiohttp.ClientSession() as session:

        tasks = []

        for source in RESEARCH_SOURCES:

            url = source + query

            async def worker(link):
                try:
                    async with session.get(link, timeout=5) as response:
                        if response.status == 200:
                            return link
                except:
                    return None

            tasks.append(worker(url))

        results = await asyncio.gather(*tasks)

        signals = [r for r in results if r]

    confidence = min(len(signals) * 0.35, 1.0)

    return signals, confidence

# =============================
# TELEGRAM COMMANDS
# =============================

@dp.message(Command("start"))
async def start(message: types.Message):

    if not access(message.from_user.id):
        await message.answer("⛔ Closed Research Bot")
        return

    await message.answer("""
🤖 Research OSINT Bot

Commands:
/scan username
""")

@dp.message(Command("scan"))
async def scan(message: types.Message):

    if not access(message.from_user.id):
        return

    try:
        query = message.text.split()[1]

        await message.answer("🧠 Research analysis running...")

        signals, confidence = await research_engine(query)

        if signals:
            await message.answer(
                "✅ Public Signals Found:\n" +
                "\n".join(signals) +
                f"\n🎯 Confidence Score: {confidence:.2f}"
            )
        else:
            await message.answer("❌ No public signals detected")

    except:
        await message.answer("Usage: /scan username")

# =============================
# MAIN LOOP
# =============================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
