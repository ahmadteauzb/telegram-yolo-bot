import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ContentType
from ultralytics import YOLO
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# Environment variables
BOT_TOKEN = os.getenv("7752872578:AAG915cbkcOBkBspD-yZwigLLyH6tgelJLg")
SPREADSHEET_ID = os.getenv("1yna6vnX75cUJl-tNQkEtl_h1pkfGJzsuZdS80nt584Y")
MODEL_PATH = os.getenv("MODEL_PATH", "yolov8n.pt")

# Logging setup
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Load YOLO model
yolo_model = YOLO(MODEL_PATH)

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.reply("Assalomu alaykum! Rasmlarni jo‘nating va men ularni tahlil qilib beraman!")

@dp.message(lambda message: message.photo)
async def handle_photo(message: Message):
    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        # Download image
        image_name = f"image_{int(time.time())}.jpg"
        await bot.download_file(file_path, image_name)
        
        # Process image with YOLO
        results = yolo_model(image_name)
        detections = results[0].boxes.data.tolist()
        
        detected_items = []
        for detection in detections:
            x1, y1, x2, y2, conf, cls = detection
            label = yolo_model.names[int(cls)]
            confidence = round(conf * 100, 2)
            detected_items.append((label, confidence))
        
        # Log and send response
        response_text = "\n".join([f"{item[0]} - {item[1]}%" for item in detected_items])
        await message.reply(f"Aniqlangan mahsulotlar:\n{response_text}")
        
        # Save results to Google Sheets
        for item in detected_items:
            sheet.append_row([time.strftime("%Y-%m-%d %H:%M:%S"), image_name, file_url, item[0], item[1]])
        
        # Cleanup
        os.remove(image_name)
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        await message.reply("Xatolik yuz berdi, iltimos, boshqa rasm yuboring.")

async def main():
    print("🚀 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
