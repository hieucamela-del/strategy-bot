import os
from dotenv import load_dotenv

load_dotenv()

APP_MODE = os.getenv("APP_MODE", None) or os.getenv("APP_MODE", "PAPER")
ALLOWED_DIRECTIONS = [d.strip().upper() for d in (os.getenv("ALLOWED_DIRECTIONS") or "BUY,SELL").split(",") if d.strip()]
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "0.60"))
MAX_POSITION_PCT = float(os.getenv("MAX_POSITION_PCT", "0.05"))
MAX_DAILY_TRADES = int(os.getenv("MAX_DAILY_TRADES", "10"))
INPUT_FINBOX = os.getenv("INPUT_FINBOX", "data/finbox_notifications.json")
INPUT_ZALO = os.getenv("INPUT_ZALO", "data/zalo_script.txt")
ACCOUNT_FILE = os.getenv("ACCOUNT_FILE", "data/account.json")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
PRINT_LOGS = os.getenv("PRINT_LOGS", "true").lower() == "true"

# New settings from config.yaml or env
CONTRACTS_PER_ORDER = int(os.getenv("CONTRACTS_PER_ORDER", "0"))  # 0 -> compute by % vốn
ENTRY_WINDOW_START = os.getenv("ENTRY_WINDOW_START", "09:00")  # "HH:MM"
ENTRY_WINDOW_END = os.getenv("ENTRY_WINDOW_END", "15:00")
CLOSE_TIME = os.getenv("CLOSE_TIME", "14:30")

# AUTH settings
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"
AUTH_USER = os.getenv("AUTH_USER", "admin")
AUTH_PASS = os.getenv("AUTH_PASS", "changeme")
