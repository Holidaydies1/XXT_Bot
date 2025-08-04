
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

# Tokens & IDs
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = "@xxt_hub"
SUPPORT_CHAT_URL = "https://t.me/xxt_support"
ADMIN_CHAT_ID = -1001234567890
SUPPORT_CHAT_ID = -1002222222222
ADMIN_ID = 123456789  # Replace with your Telegram ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Health-check
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

# Load phrases & changelog
def load_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

phrases = load_file("phrases.txt")
changelog = "\n".join(load_file("changelog.txt"))
phrase_index = 0

# Keyboards
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📢 Join our Channel", url="https://t.me/xxt_hub"),
        InlineKeyboardButton("💡 Get Motivation", callback_data="get_motivation"),
        InlineKeyboardButton("❓ FAQ", callback_data="faq_menu"),
        InlineKeyboardButton("🆕 Changelog", callback_data="changelog"),
        InlineKeyboardButton("🛠 Support", callback_data="support_menu")
    )
    return keyboard

def support_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("✍️ Ask a Question", callback_data="create_ticket"),
        InlineKeyboardButton("⬅ Back", callback_data="back_to_main")
    )
    return keyboard

def faq_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Binance", callback_data="faq_binance"),
        InlineKeyboardButton("KuCoin", callback_data="faq_kucoin"),
        InlineKeyboardButton("Bybit", callback_data="faq_bybit"),
        InlineKeyboardButton("⬅ Back", callback_data="back_to_main")
    )
    return keyboard

# Daily motivation
async def daily_post():
    global phrase_index
    while True:
        now = datetime.now()
        target_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
        if now > target_time:
            target_time += timedelta(days=1)
        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)
        if phrases:
            phrase = phrases[phrase_index % len(phrases)]
            phrase_index += 1
        else:
            phrase = "Stay motivated!"
        await bot.send_message(CHANNEL_ID, f"**Daily Motivation:**\n{phrase}", parse_mode="Markdown")

# Callbacks
@dp.callback_query_handler(lambda c: c.data == "get_motivation")
async def get_motivation(callback_query: types.CallbackQuery):
    await callback_query.answer()
    phrase = random.choice(phrases) if phrases else "Stay motivated!"
    await callback_query.message.answer(f"**Motivation:**\n{phrase}", parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == "support_menu")
async def show_support(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("🛠 Support Menu:", reply_markup=support_menu())

@dp.callback_query_handler(lambda c: c.data == "faq_menu")
async def show_faq(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("❓ FAQ Categories:", reply_markup=faq_menu())

@dp.callback_query_handler(lambda c: c.data.startswith("faq_"))
async def faq_handler(callback_query: types.CallbackQuery):
    faq_type = callback_query.data.split("_")[1]
    if faq_type == "binance":
        text = "Binance FAQ:\n1. Register with our link.\n2. Complete KYC.\n3. Deposit and start trading."
    else:
        text = f"{faq_type.capitalize()} FAQ is coming soon."
    await callback_query.message.edit_text(text, reply_markup=faq_menu())

@dp.callback_query_handler(lambda c: c.data == "changelog")
async def show_changelog(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(f"**Changelog:**\n{changelog}", parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == "create_ticket")
async def create_ticket(callback_query: types.CallbackQuery):
    await callback_query.message.answer("✍️ Please describe your issue in one message. Our team will contact you.")
    dp.register_message_handler(handle_ticket, state=None)

async def handle_ticket(message: types.Message):
    await bot.send_message(ADMIN_CHAT_ID, f"📩 *New Ticket* from {message.from_user.full_name} (@{message.from_user.username}):\n\n{message.text}", parse_mode="Markdown")
    await message.answer("✅ Your ticket has been sent! Our team will contact you soon.")
    dp.message_handlers.unregister(handle_ticket)

@dp.callback_query_handler(lambda c: c.data == "back_to_main")
async def back_to_main(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("👋 Welcome back to **XXT Crypto Hub**!", reply_markup=main_menu(), parse_mode="Markdown")

# Commands
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("👋 Welcome to **XXT Crypto Hub**!", reply_markup=main_menu(), parse_mode="Markdown")

@dp.message_handler(commands=['news'])
async def news(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        content = message.text.replace("/news", "").strip()
        if content:
            await bot.send_message(CHANNEL_ID, content)
            await message.answer("✅ News sent.")
        else:
            await message.answer("❌ Please provide text for news.")
    else:
        await message.answer("❌ You are not authorized.")

@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📊 Stats feature coming soon.")
    else:
        await message.answer("❌ You are not authorized.")

# Default handler
@dp.message_handler()
async def log_messages(message: types.Message):
    logging.info(f"User {message.from_user.id} wrote: {message.text}")
    await message.answer("Thank you for your message! Use /start to open the menu.")

# Run
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(daily_post())
    executor.start_polling(dp, skip_updates=True)
