# utils/download_and_upload.py
import os
import requests
from telegram import InputMediaPhoto

TEMP_IMAGE_DIR = 'temp_images/'

def download_image(image_path):
    if not os.path.exists(TEMP_IMAGE_DIR):
        os.makedirs(TEMP_IMAGE_DIR)
    
    image_url = f"https://image.tmdb.org/t/p/w500{image_path}"
    response = requests.get(image_url)
    
    if response.status_code == 200:
        image_file_path = os.path.join(TEMP_IMAGE_DIR, os.path.basename(image_path))
        with open(image_file_path, 'wb') as f:
            f.write(response.content)
        return image_file_path
    return None

async def upload_images_and_send_message_1(update, movie_data, context):
    poster_file_path = download_image(movie_data['poster_path'])
    backdrop_file_path = download_image(movie_data['backdrop_path'])

    if poster_file_path and backdrop_file_path:
        # Prepare the movie information text
        movie_info_text = (
            f"*{movie_data['title_en']} ({movie_data['year_en']})*\n"
            f"*{movie_data['title_ru']} ({movie_data['year_ru']})*\n\n"
            f"🍿 IMDB: {movie_data['rating']}\n\n"
            f"*Сюжет (RU):*\n{movie_data['description_ru']}\n\n"
            f"*Premise (EN):*\n{movie_data['description_en']}\n\n"
            f"🎬 [Trailer]({movie_data['trailer_url']})\n"
        )

        # Add the watch link if available
        if movie_data.get('watch_link'):
            movie_info_text += f"🔗 [Watch here]({movie_data['watch_link']})\n\n"

        movie_info_text += (
            "\n\n📺 [Cinemates](https://t.me/cinemates_og)\n"
        )

        # Prepare media group (poster and backdrop with one caption)
        media = [
            InputMediaPhoto(open(poster_file_path, 'rb'), caption=movie_info_text, parse_mode='Markdown'),
            InputMediaPhoto(open(backdrop_file_path, 'rb'))
        ]
        
        await update.message.reply_media_group(media)
        
        os.remove(poster_file_path)
        os.remove(backdrop_file_path)
    else:
        await update.message.reply_text('Не удалось загрузить постер или фон.')
