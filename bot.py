from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
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
ADMIN_CHAT_ID = -1001234567890  # Replace with your admin group ID
SUPPORT_CHAT_ID = -1002222222222  # Replace with actual group ID
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

def load_changelog():
    try:
        with open("changelog.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "No updates logged yet."

# ---------- Keyboards ----------
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📢 Join our Channel", url="https://t.me/xxt_hub"),
        InlineKeyboardButton("🎓 Buy a Course", url="https://yourcoursepaymentlink.com"),
        InlineKeyboardButton("💎 Buy a Subscription", url="https://yoursubscriptionlink.com"),
        InlineKeyboardButton("ℹ️ About Us", callback_data="about_us"),
        InlineKeyboardButton("💬 Support Chat", url=SUPPORT_CHAT_URL),
        InlineKeyboardButton("🛠 Support Menu", callback_data="support_menu"),
        InlineKeyboardButton("🆕 Changelog", callback_data="changelog")
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

def back_menu():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("⬅ Back to Menu", callback_data="back_to_main"))

# ---------- Reply Keyboard (Persistent buttons) ----------
def navigation_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(
        KeyboardButton("About Us"),
        KeyboardButton("Motivation"),
        KeyboardButton("Crypto Tip"),
        KeyboardButton("Support")
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

        if datetime.now().day % 3 == 0:
            await bot.send_poll(
                CHANNEL_ID,
                question="Which topic should we cover next?",
                options=["Trading basics", "Market analysis", "Crypto tools", "Motivational tips"],
                is_anonymous=True
            )

# ---------- Auto post changelog to channel on start ----------
async def post_changelog_to_channel():
    changelog = load_changelog()
    if changelog.strip():
        await bot.send_message(CHANNEL_ID, f"**🚀 XXT Bot has been updated!**\n\n{changelog}", parse_mode="Markdown")

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

# ---------- Callbacks ----------
@dp.callback_query_handler(lambda c: c.data == "support_menu")
async def show_support_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("🛠 Support Menu:", reply_markup=support_menu())

@dp.callback_query_handler(lambda c: c.data == "faq")
async def show_faq(callback_query: types.CallbackQuery):
    faq_content = load_faq()
    await callback_query.message.edit_text(f"**FAQ:**\n\n{faq_content}", reply_markup=back_menu(), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == "changelog")
async def show_changelog(callback_query: types.CallbackQuery):
    changelog = load_changelog()
    await callback_query.message.edit_text(f"**Bot Updates:**\n\n{changelog}", reply_markup=back_menu(), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == "about_us")
async def show_about(callback_query: types.CallbackQuery):
    about_text = (
        "🤖 **About XXT Bot**\n\n"
        "XXT Hub is your trusted partner for crypto knowledge, motivation, and growth.\n\n"
        "Here’s what we offer:\n"
        "- Daily insights and motivational posts\n"
        "- Guides for beginners and experts\n"
        "- Exclusive courses and tools\n"
        "- Direct support and community chat\n\n"
        "Stay connected and grow with us!"
    )
    await callback_query.message.edit_text(about_text, reply_markup=back_menu(), parse_mode="Markdown")

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

# ---------- Welcome in support chat ----------
@dp.message_handler(content_types=['new_chat_members'])
async def greet_new_members(message: types.Message):
    if message.chat.id == SUPPORT_CHAT_ID:
        for new_member in message.new_chat_members:
            await message.reply(
                f"👋 Welcome, {new_member.full_name}!\n\n"
                f"Please check out our FAQ with /start in the bot or ask your question here."
            )

@dp.message_handler()
async def log_messages(message: types.Message):
    logging.info(f"User {message.from_user.id} wrote: {message.text}")
    await message.answer("Thank you for your message! Use /start to open the menu.")

# ---------- Run ----------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(post_changelog_to_channel())
    loop.create_task(daily_post())
    executor.start_polling(dp, skip_updates=True)
