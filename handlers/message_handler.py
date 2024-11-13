# handlers/message_handler.py

import random
from telegram import Update
from telegram.ext import ContextTypes
from utils.fetch_movie_data import fetch_top_movies_by_genre, fetch_movie_data
from utils.download_and_upload import upload_images_and_send_message_1
from utils.download_and_upload_top_posters import upload_images_and_send_message

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        title, year = map(str.strip, text.split(','))
        movie_data = fetch_movie_data(title, year)

        if movie_data:
            await upload_images_and_send_message_1(update, movie_data, context)
        else:
            await update.message.reply_text('Фильм не найден. Пожалуйста, попробуйте другой запрос.')
    except ValueError:
        await update.message.reply_text('Ошибка! Пожалуйста, введите данные в формате: "название, год".')


import random

# handler for top movies by genre
async def handle_top_movies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        _, genre = text.split(maxsplit=1)
        genre = genre.strip().capitalize()

        # Check if 'Random' is specified in the genre
        is_random = genre.startswith("Random")

        genre_mapping = {
            'Action': 28, 'Adventure': 12, 'Animation': 16, 'Comedy': 35, 'Crime': 80,
            'Documentary': 99, 'Drama': 18, 'Family': 10751, 'Fantasy': 14, 'History': 36,
            'Horror': 27, 'Music': 10402, 'Mystery': 9648, 'Romance': 10749,
            'Science Fiction': 878, 'Thriller': 53, 'War': 10752, 'Western': 37
        }

        genre_id = genre_mapping.get(genre) if not is_random else None
        movies = fetch_top_movies_by_genre(genre_id)

        if movies:
            movie_data_list = []
            for movie in movies:
                title_en = movie['title']
                year = movie['release_date'][:4]  # Extract year
                movie_data = fetch_movie_data(title_en, year)  # Fetch detailed movie data
                
                if movie_data:
                    movie_data_list.append(movie_data)

            if movie_data_list:
                await upload_images_and_send_message(update, movies, context)

                # Define headers for English and Russian
                headers_en = [
                    f"🎬 Discover the Best of {genre} Cinema, Curated by Movie Fans!",
                    f"🍿 Top-Rated {genre} Movies You Can't Miss, Selected by the Audience!",
                    f"🎥 Dive into the World of {genre} with These Fan Favorites!",
                    f"📽️ Explore the Most Loved {genre} Films, Rated by Viewers!",
                    f"🎞️ Uncover the Highest Rated {genre} Movies, Handpicked for You!"
                ]

                headers_ru = [
                    f"🎬 Откройте лучшие фильмы в жанре {genre}, выбранные зрителями!",
                    f"🍿 Топовые фильмы в жанре {genre}, которые стоит посмотреть, по мнению аудитории!",
                    f"🎥 Погрузитесь в мир {genre} с этими любимыми фильмами зрителей!",
                    f"📽️ Исследуйте самые популярные фильмы в жанре {genre}, по оценке зрителей!",
                    f"🎞️ Откройте для себя самые высокооцененные фильмы в жанре {genre}, специально для вас!"
                ]

                # Select random headers
                header_en = random.choice(headers_en)
                header_ru = random.choice(headers_ru)

                # Prepare the message text
                message_text = (
                    f"*{header_en}\n\n{header_ru}*\n\n"
                )
                for movie_data in movie_data_list:
                    message_text += (
                        f"> **{movie_data['title_en']} ({movie_data['year_en']})**\n"
                        f"> **{movie_data['title_ru']} ({movie_data['year_ru']})**\n"
                        f"> 🍿 **IMDB:** {movie_data['rating']}\n"
                        f"> 🎬 [Trailer]({movie_data['trailer_url']})\n"
                        "------------\n"
                    )

                # Add channel link
                message_text += (
                    "\n\n📺 [Cinemates](https://t.me/cinemates_og)\n"
                )

                # Send the message
                await update.message.reply_text(message_text, disable_web_page_preview=True, parse_mode='Markdown')
            else:
                await update.message.reply_text('Ошибка при получении информации о фильмах.')
        else:
            await update.message.reply_text('Нет фильмов для данного жанра.' if not is_random else 'Нет доступных случайных фильмов.')
    except Exception as e:
        await update.message.reply_text('Ошибка! Пожалуйста, проверьте свой ввод.')