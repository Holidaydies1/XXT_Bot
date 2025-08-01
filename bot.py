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
ADMIN_CHAT_ID = -1001234567890  # Replace with your admin group ID
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

# ---------- Load content ----------
def load_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

phrases = load_file("phrases.txt")
cta = load_file("cta.txt")
crypto_tips = load_file("crypto_tips.txt")

def load_faq():
    try:
        with open("faq.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "FAQ is empty. Please add content to faq.txt."

# ---------- Keyboards ----------
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📢 Join our Channel", url="https://t.me/xxt_hub"),
        InlineKeyboardButton("🎓 Buy a Course", url="https://yourcoursepaymentlink.com"),
        InlineKeyboardButton("💎 Buy a Subscription", url="https://yoursubscriptionlink.com"),
        InlineKeyboardButton("🛠 Support", callback_data="support_menu")
    )
    return keyboard

def support_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📚 FAQ", callback_data="faq"),
        InlineKeyboardButton("✍️ Create Ticket", callback_data="create_ticket"),
        InlineKeyboardButton("⬅ Back", callback_data="back_to_main")
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
    await message.answer(
        "👋 Welcome to **XXT Crypto Hub**!\n\nChoose an option below:",
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

@dp.message_handler(commands=['motivation'])
async def motivation(message: types.Message):
    phrase = random.choice(phrases) if phrases else "Stay motivated!"
    await message.answer(f"**Motivation:**\n{phrase}", parse_mode="Markdown")

@dp.message_handler(commands=['cryptotip'])
async def cryptotip(message: types.Message):
    tip = random.choice(crypto_tips) if crypto_tips else "Pro tip: Always do your own research."
    await message.answer(f"**Crypto Tip:**\n{tip}", parse_mode="Markdown")

# ---------- Support ----------
@dp.callback_query_handler(lambda c: c.data == "support_menu")
async def show_support_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("🛠 Support Menu:", reply_markup=support_menu())

@dp.callback_query_handler(lambda c: c.data == "faq")
async def show_faq(callback_query: types.CallbackQuery):
    faq_content = load_faq()
    await callback_query.message.edit_text(f"**FAQ:**\n\n{faq_content}", parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == "create_ticket")
async def create_ticket(callback_query: types.CallbackQuery):
    await callback_query.message.answer("✍️ Please describe your issue in one message. Our team will contact you.")
    dp.register_message_handler(handle_ticket, state=None)

async def handle_ticket(message: types.Message):
    await bot.send_message(ADMIN_CHAT_ID, f"📩 *New Support Ticket* from {message.from_user.full_name} (@{message.from_user.username}):\n\n{message.text}", parse_mode="Markdown")
    await message.answer("✅ Your ticket has been sent! Our team will contact you soon.")
    dp.message_handlers.unregister(handle_ticket)

@dp.callback_query_handler(lambda c: c.data == "back_to_main")
async def back_to_main(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("👋 Welcome back to **XXT Crypto Hub**!", reply_markup=main_menu(), parse_mode="Markdown")

@dp.message_handler()
async def log_messages(message: types.Message):
    logging.info(f"User {message.from_user.id} wrote: {message.text}")
    await message.answer("Thank you for your message! Use /start to open the menu.")

# ---------- Run ----------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(daily_post())
    executor.start_polling(dp, skip_updates=True)
