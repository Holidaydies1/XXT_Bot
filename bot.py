from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import os
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
import asyncio
import random
from datetime import datetime, timedelta

# Logging
logging.basicConfig(level=logging.INFO)

# Token & Channel
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = "@xxt_hub"  # our channel
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ---------- Health-check for Render ----------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    server_address = ('', 10000)
    httpd = HTTPServer(server_address, HealthHandler)
    httpd.serve_forever()

Thread(target=run_server, daemon=True).start()
# ---------------------------------------------

# ---------- Load content from files ----------
def load_phrases(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

phrases = load_phrases("phrases.txt")  # motivational quotes
cta = load_phrases("cta.txt")  # call-to-actions
crypto_tips = load_phrases("crypto_tips.txt")  # crypto tips
# ---------------------------------------------

# ---------- Main menu ----------
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📢 Join our channel", url="https://t.me/xxt_hub"),
        InlineKeyboardButton("🎓 Buy a course", url="https://yourcoursepaymentlink.com"),
        InlineKeyboardButton("💎 Get a subscription", url="https://yoursubscriptionlink.com")
    )
    return keyboard

# ---------- Daily posts ----------
async def daily_post():
    await bot.send_message(CHANNEL_ID, "👋 XXT Bot is back online. Stay tuned for updates!")
    while True:
        now = datetime.now()
        target_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
        if now > target_time:
            target_time += timedelta(days=1)
        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)

        phrase = random.choice(phrases) if phrases else "Stay motivated!"
        call_to_action = random.choice(cta) if cta else "💡 Want to grow? Chat with me in @XXTCryptoBot"
        tip = random.choice(crypto_tips) if crypto_tips else "Pro tip: Never invest more than you can afford to lose."

        post_text = f"**{phrase}**\n\n{tip}\n\n{call_to_action}"
        await bot.send_message(CHANNEL_ID, post_text, parse_mode="Markdown")

        # Poll every 3 days
        if datetime.now().day % 3 == 0:
            await bot.send_poll(
                CHANNEL_ID,
                question="Which topic should we cover next?",
                options=["Trading basics", "Market analysis", "Crypto tools", "Motivational tips"],
                is_anonymous=True
            )

# ---------- Commands ----------
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    logging.info(f"User {message.from_user.id} wrote /start")
    await message.answer(
        "👋 Welcome to **XXT Crypto Hub**!\n\nChoose an action below:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.message_handler(commands=['about'])
async def about(message: types.Message):
    await message.answer(
        "🤖 **About XXT Bot**\n\n"
        "XXT Hub is your gateway to crypto knowledge, daily motivation, and personal growth.\n"
        "We provide:\n"
        "- Daily insights and motivational posts\n"
        "- Guides for beginners and experts\n"
        "- Exclusive courses and tools\n\n"
        "Stay connected and grow with us!",
        parse_mode="Markdown"
    )

@dp.message_handler()
async def log_messages(message: types.Message):
    logging.info(f"User {message.from_user.id} wrote: {message.text}")
    await message.answer("Thank you for your message! Use /start to open the menu.")

# ---------- Run ----------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(daily_post())
    executor.start_polling(dp, skip_updates=True)
