# utils/fetch_movie_data.py

from translate import Translator
from langdetect import detect
import requests
import config
import random

def translate_to_russian(text):
    try:
        # Initialize a translator to translate to Russian
        translator = Translator(to_lang="ru")
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# Function to fetch movie data from TMDb API
def fetch_movie_data(title, year):
    url_en = f'https://api.themoviedb.org/3/search/movie?api_key={config.TMDB_API_KEY}&query={title}&year={year}&language=en-US'
    url_ru = f'https://api.themoviedb.org/3/search/movie?api_key={config.TMDB_API_KEY}&query={title}&year={year}&language=ru-RU'
    
    response_en = requests.get(url_en)
    response_ru = requests.get(url_ru)

    if response_en.status_code == 200 and response_ru.status_code == 200:
        data_en = response_en.json()
        data_ru = response_ru.json()
        
        if data_en['results'] and data_ru['results']:
            movie_en = data_en['results'][0]  # Get the first result for English
            movie_ru = data_ru['results'][0]  # Get the first result for Russian
            
            # Get the movie ID for fetching videos
            movie_id = movie_en.get('id')
            trailer_url = get_trailer_url(movie_id)
            watch_link = get_watch_link(movie_id)

            # Get the Russian description
            description_ru = movie_ru.get('overview', movie_en.get('overview'))

            # Detect the language of the Russian description
            if detect(description_ru) == 'en':
                print("Russian description is in English, translating to Russian...")
                description_ru = translate_to_russian(description_ru)

            return {
            'title_en': movie_en.get('title'),
            'description_en': movie_en.get('overview'),
            'year_en': movie_en.get('release_date')[:4],
            'rating': movie_en.get('vote_average'),
            'poster_path': movie_en.get('poster_path'),
            'backdrop_path': movie_en.get('backdrop_path'),
            'title_ru': movie_ru.get('title', movie_en.get('title')),
            'description_ru': description_ru,  # Use the translated description if needed
            'year_ru': movie_ru.get('release_date', movie_en.get('release_date'))[:4],
            'trailer_url': trailer_url,
            'watch_link': watch_link  # Include watch link in the returned data
            }
        else:
            return None
    else:
        return None

# Function to get the watch link (where to watch the movie)
def get_watch_link(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={config.TMDB_API_KEY}'
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and 'RU' in data['results']:
            ru_provider = data['results']['RU'].get('link')
            if ru_provider:
                return ru_provider
        if 'results' in data and 'US' in data['results']:
            en_provider = data['results']['US'].get('link')
            if en_provider:
                return en_provider
    
    return None

# Function to get trailer URL
def get_trailer_url(movie_id):
    # Try to get the trailer in Russian
    url_ru = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={config.TMDB_API_KEY}&language=ru-RU'
    url_en = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={config.TMDB_API_KEY}&language=en-US'
    
    # Fetch Russian trailer first
    response_ru = requests.get(url_ru)
    if response_ru.status_code == 200:
        videos_ru = response_ru.json().get('results', [])
        for video in videos_ru:
            if video['type'] == 'Trailer':
                return f"https://www.youtube.com/watch?v={video['key']}"
    
    # Fallback to English trailer if no Russian trailer is found
    response_en = requests.get(url_en)
    if response_en.status_code == 200:
        videos_en = response_en.json().get('results', [])
        for video in videos_en:
            if video['type'] == 'Trailer':
                return f"https://www.youtube.com/watch?v={video['key']}"
    
    return None

def fetch_random_movies():
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={config.TMDB_API_KEY}&sort_by=popularity.desc'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return random.sample(data['results'], 5)  # Return 5 random movies
    else:
        return None

def fetch_top_movies_by_genre(genre_id=None):
    if genre_id:
        url = f'https://api.themoviedb.org/3/discover/movie?api_key={config.TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc'
    else:
        return fetch_random_movies()  # Fetch random movies if no genre is specified

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['results'][:5]  # Return top 5 movies
    else:
        return None