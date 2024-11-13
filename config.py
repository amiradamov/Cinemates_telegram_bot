from dotenv import load_dotenv
import os

# Load environment variables from the .env file (for local development)
load_dotenv()

# Get values from the environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")