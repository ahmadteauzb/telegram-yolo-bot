import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from aiogram.utils import executor
from ultralytics import YOLO
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
MODEL_PATH = os.getenv("MODEL_PATH", "yolov8n.pt")

# Logging setup
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Load YOLO model
yolo_model = YOLO(MODEL_PATH)

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

async def process_image(message: types.Message):
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

@dp.message_handler(content_types=ContentType.PHOTO)
async def handle_photo(message: types.Message):
    await process_image(message)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

