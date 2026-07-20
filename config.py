import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("ISI_TOKEN_TELEGRAM")
BOT_NAME = "ohooo_bot"
BOT_USERNAME = "@ohooo_bot"

# API Keys (Optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
TENOR_API_KEY = os.getenv("TENOR_API_KEY", "")
IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID", "")

# Database
DATABASE_PATH = "data/database.db"

# Admin Settings
DEFAULT_WARN_LIMIT = 3
MUTE_DURATION = 3600  # 1 hour
SPAM_THRESHOLD = 5
SPAM_INTERVAL = 10  # seconds

# XP System
XP_PER_MESSAGE = 10
XP_COOLDOWN = 60  # seconds
LEVEL_UP_XP = 100

# Rate Limiting
RATE_LIMIT = 30  # messages per minute
COMMAND_COOLDOWN = 3  # seconds

# Feature Toggles
ENABLE_AI = False
ENABLE_GAMES = True
ENABLE_TRANSLATION = True
