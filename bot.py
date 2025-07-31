
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

API_TOKEN = 'YOUR_TOKEN_HERE'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def main_menu():
    buttons = [
        [KeyboardButton(text="📘 Get Guide")],
        [KeyboardButton(text="🎓 Lessons")],
        [KeyboardButton(text="🌐 Join XXT Community")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    welcome_text = (
        "👋 Welcome to **XXT Crypto Hub**!\n\n"
        "Your first step to mastering cryptocurrency.\n\n"
        "Choose an option below to start:"
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=main_menu())

@dp.message(lambda message: message.text == "📘 Get Guide")
async def get_guide(message: types.Message):
    await message.answer("Our PDF guide will be available soon!")

@dp.message(lambda message: message.text == "🎓 Lessons")
async def lessons(message: types.Message):
    await message.answer("Lessons section coming soon!")

@dp.message(lambda message: message.text == "🌐 Join XXT Community")
async def join(message: types.Message):
    await message.answer("Join us: https://t.me/XXTCryptoHub")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
