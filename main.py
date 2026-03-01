import asyncio
import feedparser

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F

# ================= CONFIG =================

TOKEN = "8418191088:AAFEANI4tnCVeTKo6eMheSrc2C3OVnAdC7A"

OWNER_ID = 702815281

# ================= MEMORY STORAGE =================

ALLOWED_USERS = set()
PENDING_USERS = set()

# ================= BOT =================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================= LANGUAGE STRINGS (Russian) =================

TEXTS = {
    "welcome": "🤖 Приватный бот аналитики\n\nКоманды:\n/news — новости\n/echo — повтор текста",
    "wait_approval": "⏳ Ожидайте подтверждения администратора",
    "access_denied": "⛔ Доступ запрещён",
    "approved": "✅ Доступ разрешён",
    "denied": "❌ Доступ отклонён"
}

# ================= NEWS SOURCES =================

NEWS_FEEDS = [
    "https://ria.ru/export/rss2/index.xml",
    "https://tass.ru/rss/v2.xml",
    "https://russian.rt.com/rss"
]

# ================= ACCESS CONTROL =================

def is_allowed(user_id):
    return user_id == OWNER_ID or user_id in ALLOWED_USERS

# ================= USER APPROVAL SYSTEM =================

@dp.message(Command("start"))
async def start_handler(message: types.Message):

    user_id = message.from_user.id

    if is_allowed(user_id):
        await message.answer(TEXTS["welcome"])
        return

    PENDING_USERS.add(user_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Принять",
                callback_data=f"approve_{user_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"deny_{user_id}"
            )
        ]
    ])

    await bot.send_message(
        OWNER_ID,
        f"🔔 Новый пользователь ID {user_id} хочет доступ",
        reply_markup=keyboard
    )

    await message.answer(TEXTS["wait_approval"])

# ================= ADMIN APPROVAL =================

@dp.callback_query(F.data.startswith("approve_"))
async def approve_user(callback: types.CallbackQuery):

    if callback.from_user.id != OWNER_ID:
        return

    user_id = int(callback.data.split("_")[1])

    ALLOWED_USERS.add(user_id)
    PENDING_USERS.discard(user_id)

    await bot.send_message(user_id, TEXTS["approved"])
    await callback.answer(TEXTS["approved"])

@dp.callback_query(F.data.startswith("deny_"))
async def deny_user(callback: types.CallbackQuery):

    if callback.from_user.id != OWNER_ID:
        return

    user_id = int(callback.data.split("_")[1])

    PENDING_USERS.discard(user_id)

    await bot.send_message(user_id, TEXTS["denied"])
    await callback.answer(TEXTS["denied"])

# ================= NEWS ENGINE =================

def get_news():

    news_list = []

    try:
        for feed in NEWS_FEEDS:

            parsed = feedparser.parse(feed)

            for entry in parsed.entries[:2]:

                title = entry.get("title", "")
                summary = entry.get("summary", "")

                news_list.append(
                    f"📰 {title}\n{summary[:300]}...\n"
                )

    except Exception:
        return ["Ошибка получения новостей"]

    return news_list[:5]

# ================= COMMANDS =================

@dp.message(Command("news"))
async def news_handler(message: types.Message):

    if not is_allowed(message.from_user.id):
        return

    await message.answer("\n".join(get_news()))

@dp.message(Command("echo"))
async def echo_handler(message: types.Message):

    if not is_allowed(message.from_user.id):
        return

    text = message.text.replace("/echo", "").strip()

    if not text:
        await message.answer("Введите текст после /echo")
        return

    await message.answer(text)

# ================= MAIN =================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
