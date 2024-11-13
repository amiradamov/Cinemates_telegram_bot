# utils/download_and_upload_top_posters.py
import os
import requests
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes

# Directory to save downloaded posters
POSTER_DIR = 'posters'

def download_image(image_url, poster_path):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(poster_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
        return False
    except Exception as e:
        print(f"Failed to download image: {e}")
        return False

async def upload_images_and_send_message(update: Update, movies, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not os.path.exists(POSTER_DIR):
            os.makedirs(POSTER_DIR)
        
        media_group = []
        for i, movie in enumerate(movies[:10]):  # Limit to top 10 movies to prevent message overflow
            poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
            poster_path = os.path.join(POSTER_DIR, f"poster_{i}.jpg")

            if download_image(poster_url, poster_path):
                media_group.append(InputMediaPhoto(open(poster_path, 'rb')))
        
        if media_group:
            await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group)

        # Optionally, delete downloaded posters after sending them
        for poster in os.listdir(POSTER_DIR):
            os.remove(os.path.join(POSTER_DIR, poster))
    except Exception as e:
        await update.message.reply_text(f"Ошибка при загрузке изображений: {e}")
