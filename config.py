import os

# TFL API Configuration
TFL_API_BASE_URL = "https://api.tfl.gov.uk"

# Lines to monitor
MONITORED_LINES = [
    "northern",
    "victoria",
    "london-overground"
]

# Station IDs
HIGHBURY_STATION_ID = "940GZZLUHBT"  # Highbury & Islington
WALTHAMSTOW_STATION_ID = "910GWALTMCN"  # Walthamstow Central Overground

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your-telegram-bot-token")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your-chat-id")

# Scheduler Configuration
SCHEDULES = [
    {"hour": 15, "minute": 45},
    {"hour": 16, "minute": 0}
]

# API Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
