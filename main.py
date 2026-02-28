import asyncio
import aiohttp
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ===============================
# CONFIGURATION
# ===============================

TOKEN = "8418191088:AAFEANI4tnCVeTKo6eMheSrc2C3OVnAdC7A"

# whitelist users
ALLOWED_USERS = {
    702815281
}

# ===============================
# BOT INIT
# ===============================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===============================
# PUBLIC RESEARCH SOURCES
# ===============================

SOURCES = [
    "https://github.com/",
    "https://t.me/",
    "https://reddit.com/user/"
]

# ===============================
# ACCESS CONTROL
# ===============================

def is_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USERS

# ===============================
# RESEARCH ENGINE
# ===============================

async def research_engine(query: str):

    signals = []

    try:
        async with aiohttp.ClientSession() as session:

            tasks = []

            for source in SOURCES:

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

    except Exception:
        pass

    confidence = min(len(signals) * 0.4, 1.0)

    return signals, confidence

# ===============================
# TELEGRAM COMMANDS
# ===============================

@dp.message(Command("start"))
async def start(message: types.Message):

    if not is_allowed(message.from_user.id):
        await message.answer("⛔ Access denied")
        return

    await message.answer("""
🤖 Research Bot Active

Commands:
/scan username
""")

@dp.message(Command("scan"))
async def scan(message: types.Message):

    if not is_allowed(message.from_user.id):
        return

    try:
        query = message.text.split()[1]

        await message.answer("🧠 Research processing...")

        signals, confidence = await research_engine(query)

        if signals:
            await message.answer(
                "✅ Public signals:\n" +
                "\n".join(signals) +
                f"\nConfidence: {confidence:.2f}"
            )
        else:
            await message.answer("❌ No public research signals found")

    except Exception:
        await message.answer("Usage: /scan username")

# ===============================
# MAIN LOOP
# ===============================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
