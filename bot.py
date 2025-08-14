# ===========================
# XXT Telegram Bot (aiogram)
# Ready for Render + UptimeRobot
# Language: EN (all user-facing text)
# ===========================

import os
import asyncio
import logging
from datetime import datetime, timedelta
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ---------- Tokens & IDs ----------
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("API_TOKEN is not set")

# can be @username or numeric id -100XXXXXXXXXX
CHANNEL_ID = os.getenv("CHANNEL_ID", "@xxt_hub")
SUPPORT_CHAT_URL = os.getenv("SUPPORT_CHAT_URL", "https://t.me/xxt_support")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "-1001234567890"))
SUPPORT_CHAT_ID = int(os.getenv("SUPPORT_CHAT_ID", "-1002222222222"))

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# ---------- Health-check for Render (anti-sleep) ----------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info("[PING] Received ping from uptime monitor")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return  # silence default http.server logs

def run_server():
    port = int(os.getenv("PORT", os.getenv("PING_PORT", "10000")))
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthHandler)
    logging.info(f"[HEALTH] Anti-sleep server started on port {port}")
    httpd.serve_forever()

# ---------- Load content ----------
def load_file(file_name: str):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

quotes = load_file("phrases.txt") or [
    "You are stronger than you think.",
    "Small steps daily = big changes.",
    "Discipline beats motivation."
]
cta_lines = load_file("cta.txt") or [
    "Join our channel for daily insights."
]
crypto_tips = load_file("crypto_tips.txt") or [
    "Never invest money you can’t afford to lose.",
    "Do your own research (DYOR) and diversify risk."
]

# ---------- Keyboards ----------
def main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔥 Channel", url=os.getenv("TG_CHANNEL_URL", "https://t.me/xxt_hub")),
        InlineKeyboardButton("💬 Chat", url=os.getenv("TG_CHAT_URL", "https://t.me/xxt_support")),
        InlineKeyboardButton("🎬 TikTok", url=os.getenv("TT_URL", "https://tiktok.com/@xxt")),
        InlineKeyboardButton("▶️ YouTube", url=os.getenv("YT_URL", "https://youtube.com/@xxt")),
        InlineKeyboardButton("📘 Facebook", url=os.getenv("FB_URL", "https://facebook.com/xxt")),
    )
    return kb

# ---------- Commands ----------
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    logger.info(f"[USER] /start from {message.from_user.id}")
    text = (
        "Hi! This is the <b>XXT</b> bot.\n"
        "Pick where you want to go 👇"
    )
    await message.answer(text, reply_markup=main_kb())

@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    await message.answer(
        "/start — main menu\n"
        "/motivation — random quote\n"
        "/cryptotip — crypto tip\n"
        "/about — about XXT + links"
    )

@dp.message_handler(commands=['motivation'])
async def cmd_motivation(message: types.Message):
    import random
    await message.answer(random.choice(quotes))

@dp.message_handler(commands=['cryptotip'])
async def cmd_cryptotip(message: types.Message):
    import random
    await message.answer("💡 " + random.choice(crypto_tips))

@dp.message_handler(commands=['about'])
async def cmd_about(message: types.Message):
    txt = (
        "<b>XXT Crew</b> — motivation, productivity, mental well‑being.\n\n"
        "Follow us:\n"
        f"• Channel: {os.getenv('TG_CHANNEL_URL','https://t.me/xxt_hub')}\n"
        f"• Chat: {os.getenv('TG_CHAT_URL','https://t.me/xxt_support')}\n"
        f"• TikTok: {os.getenv('TT_URL','https://tiktok.com/@xxt')}\n"
        f"• YouTube: {os.getenv('YT_URL','https://youtube.com/@xxt')}\n"
        f"• Facebook: {os.getenv('FB_URL','https://facebook.com/xxt')}\n"
    )
    await message.answer(txt, disable_web_page_preview=True)

# ---------- Support chat welcome ----------
@dp.message_handler(content_types=['new_chat_members'])
async def greet_new_members(message: types.Message):
    if message.chat.id == SUPPORT_CHAT_ID:
        for u in message.new_chat_members:
            await message.reply(
                f"👋 Welcome, {u.full_name}!\n"
                f"Use /help in the bot for FAQ. Ask here if you need help."
            )

# ---------- Log any text (guard) ----------
@dp.message_handler()
async def log_messages(message: types.Message):
    logging.info(f"User {message.from_user.id} wrote: {message.text}")
    await message.answer("Thanks! Use /start to open the menu.")

# ---------- Simple schedulers (optional) ----------
async def post_changelog_to_channel():
    # placeholder: post updates periodically if needed
    while True:
        await asyncio.sleep(3600)

async def daily_post():
    # daily quote to channel (UTC + optional shift)
    hour = int(os.getenv("DAILY_HOUR", "9"))
    minute = int(os.getenv("DAILY_MINUTE", "0"))
    tz_shift_minutes = int(os.getenv("DAILY_TZ_SHIFT_MIN", "0"))

    def seconds_until_next():
        now = datetime.utcnow() + timedelta(minutes=tz_shift_minutes)
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return (target - now).total_seconds()

    while True:
        wait = max(5, int(seconds_until_next()))
        logging.info(f"[SCHED] Next daily post in {wait}s")
        await asyncio.sleep(wait)
        try:
            import random
            text = "🧠 " + random.choice(quotes)
            if CHANNEL_ID:
                await bot.send_message(CHANNEL_ID, text)
                logging.info("[SCHED] Posted daily quote to channel")
        except Exception as e:
            logging.exception(f"[SCHED] Failed to post: {e}")
            await asyncio.sleep(10)

# ---------- Run ----------
if __name__ == "__main__":
    logging.info("[START] Bot is running and ready to work")

    # 1) anti-sleep HTTP server (for Render + UptimeRobot)
    Thread(target=run_server, daemon=True).start()

    # 2) schedulers (comment out if not needed)
    loop = asyncio.get_event_loop()
    loop.create_task(post_changelog_to_channel())
    loop.create_task(daily_post())

    # 3) start polling
    executor.start_polling(dp, skip_updates=True)
