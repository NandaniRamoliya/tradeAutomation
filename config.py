import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STOCKS_UNIVERSE_PATH = DATA_DIR / "stocks_nifty.json"
ENV_FILE_PATH = BASE_DIR / ".env"

# Load .env file manually if present
if ENV_FILE_PATH.exists():
    with open(ENV_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

# ==========================================
# THE SHIELD CONFIGURATION (Risk Rules)
# ==========================================
# Your total wallet capital allocated for trading in Groww (in INR)
# Default is ₹5,000, but can be updated anytime or passed as an argument.
DEFAULT_CAPITAL_INR = float(os.getenv("TRADE_CAPITAL", "5000.0"))

# Max risk allowed on any single trade (e.g., 2% of ₹5,000 = ₹100 max loss)
MAX_RISK_PER_TRADE_PCT = float(os.getenv("MAX_RISK_PCT", "2.0")) / 100.0

# Minimum acceptable Risk-to-Reward Ratio (e.g. 2.0 means aim for ₹2 gain for every ₹1 risked)
MIN_RISK_REWARD_RATIO = 2.0

# Max holding window for trades (in trading days)
MAX_HOLDING_DAYS = 2  # BTST (Buy Today, Sell Tomorrow) or 2-day momentum

# Stop-Loss multiplier based on ATR (Average True Range)
ATR_STOP_LOSS_MULTIPLIER = 1.5

# Standard Target percentages for 1-2 day momentum
TARGET_1_PCT = 0.035  # +3.5% (Partial exit or lock in profit)
TARGET_2_PCT = 0.070  # +7.0% (Full target on strong runners)

# Optional Telegram notifications
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

