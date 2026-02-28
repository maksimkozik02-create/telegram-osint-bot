==> import asyncio
import aiohttp
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# =============================
# CONFIG
# =============================

TOKEN = "8418191088:AAFEANI4tnCVeTKo6eMheSrc2C3OVnAdC7A"

ALLOWED_USERS = {702815281}

# =============================
# BOT INIT
# =============================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =============================
# HEALTH CHECK SERVER (Render Fix)
# =============================

async def health(request):
    return web.Response(text="OK")

async def start_web_server():

    app = web.Application()
    app.router.add_get("/", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# =============================
# RESEARCH ENGINE (Public sources only)
# =============================

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

    confidence = min(len(signals) * 0.4, 1.0)

    return signals, confidence

# =============================
# COMMANDS
# =============================

@dp.message(Command("start"))
async def start(message: types.Message):

    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("⛔ Access denied")
        return

    await message.answer("""
🤖 Research Bot Active

Commands:
/scan username
""")

@dp.message(Command("scan"))
async def scan(message: types.Message):

    if message.from_user.id not in ALLOWED_USERS:
        return

    try:
        query = message.text.split()[1]

        await message.answer("🧠 Research analysis running...")

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

# =============================
# MAIN LOOP
# =============================

async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        start_web_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
