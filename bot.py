import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters import Command


# Telegram bot tokenini olish (Railway-dan o'rnatiladi)
BOT_TOKEN = os.getenv("7752872578:AAG915cbkcOBkBspD-yZwigLLyH6tgelJLg")

# Bot va dispatcher yaratish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# "salom" ga javob beradigan handler
@dp.message(Text("salom"))
async def reply_to_salom(message: types.Message):
    await message.reply("Sizga ham Assalomu alaykum!")

async def main():
    print("🚀 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
