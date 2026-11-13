import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

import config

PREFERENCES_FILE = Path(__file__).resolve().parent / "user_preferences.json"


def load_preferences() -> Dict[str, Dict[str, Any]]:
    """Loads all user preferences from disk."""
    prefs: Dict[str, Dict[str, Any]] = {}
    if PREFERENCES_FILE.exists():
        try:
            with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
                prefs = json.load(f)
        except Exception:
            prefs = {}

    # Seed default user from config if not present
    default_chat = str(config.TELEGRAM_CHAT_ID).strip()
    if default_chat and default_chat not in prefs:
        prefs[default_chat] = {
            "language": "en",
            "name": "Primary User",
            "registered_at": datetime.now().isoformat()
        }
        save_preferences(prefs)

    return prefs


def save_preferences(prefs: Dict[str, Dict[str, Any]]) -> None:
    """Saves user preferences to disk."""
    try:
        with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving preferences: {e}")


def get_user_language(chat_id: Any) -> str:
    """Returns 'en', 'hi', or 'gu' for the given chat ID (default 'en')."""
    cid = str(chat_id).strip()
    prefs = load_preferences()
    user = prefs.get(cid)
    if user and "language" in user:
        lang = str(user["language"]).lower()
        if lang in ["en", "hi", "gu"]:
            return lang
    return "en"


def set_user_language(chat_id: Any, lang: str, user_info: Optional[Dict[str, Any]] = None) -> bool:
    """Updates language for a chat ID."""
    cid = str(chat_id).strip()
    clean_lang = lang.lower().strip()
    if clean_lang not in ["en", "hi", "gu"]:
        return False

    prefs = load_preferences()
    if cid not in prefs:
        prefs[cid] = {
            "registered_at": datetime.now().isoformat()
        }

    prefs[cid]["language"] = clean_lang
    prefs[cid]["updated_at"] = datetime.now().isoformat()

    if user_info:
        for k in ["first_name", "last_name", "username"]:
            if k in user_info and user_info[k]:
                prefs[cid][k] = user_info[k]

    save_preferences(prefs)
    return True


def get_all_subscribers() -> List[str]:
    """Returns a unique list of all subscriber chat IDs."""
    prefs = load_preferences()
    subscribers = set(prefs.keys())
    default_chat = str(config.TELEGRAM_CHAT_ID).strip()
    if default_chat:
        subscribers.add(default_chat)
    return list(subscribers)
