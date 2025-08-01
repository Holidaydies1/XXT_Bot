from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import os
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# Логування
logging.basicConfig(level=logging.INFO)

# Токен із середовища
API_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ---------- Health-check для Render ----------
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

# ---------- Кнопки меню ----------
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📢 Підписатись на канал", url="https://t.me/YourChannelLink"),
        InlineKeyboardButton("🎓 Купити курс", url="https://yourcoursepaymentlink.com"),
        InlineKeyboardButton("💎 Купити підписку", url="https://yoursubscriptionlink.com")
    )
    return keyboard

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    logging.info(f"Користувач {message.from_user.id} написав /start")
    await message.answer(
        "👋 Привіт! Ласкаво просимо в **XXT Crypto Hub**!\n\nОбери дію нижче:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.message_handler()
async def log_messages(message: types.Message):
    logging.info(f"Користувач {message.from_user.id} написав: {message.text}")
    await message.answer("Дякуємо за повідомлення! Оберіть дію з меню /start.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
