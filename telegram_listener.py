import sys
import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import requests

import config
from data_fetcher import fetch_stock_data
from scanner import analyze_stock_signal
from shield import TradeShield
from symbol_resolver import resolve_stock_symbol
import localization
import user_preferences
import daily_tracker

LOG_FILE = Path(__file__).resolve().parent / "bot.log"
SCHEDULE_STATE_FILE = Path(__file__).resolve().parent / "schedule_state.json"
PID_FILE = Path(__file__).resolve().parent / "bot.pid"


def load_schedule_state() -> Dict[str, str]:
    """Loads date records for sent morning/evening updates."""
    if SCHEDULE_STATE_FILE.exists():
        try:
            with open(SCHEDULE_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_schedule_state(state: Dict[str, str]):
    """Persists date records to ensure updates are never missed or duplicated."""
    try:
        with open(SCHEDULE_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log_event(f"Error saving schedule state: {e}")


def enforce_single_instance():
    """Ensures only a single bot process is running, terminating any stale instances."""
    current_pid = os.getpid()
    if PID_FILE.exists():
        try:
            with open(PID_FILE, "r") as f:
                old_pid = int(f.read().strip())
            if old_pid != current_pid:
                import subprocess
                subprocess.run(["taskkill", "/F", "/PID", str(old_pid)], capture_output=True)
        except Exception:
            pass
    try:
        with open(PID_FILE, "w") as f:
            f.write(str(current_pid))
    except Exception:
        pass

# On Windows pythonw.exe, sys.stdout and sys.stderr are None.
# If print() is called without a valid stdout handle, pythonw terminates.
# We redirect stdout/stderr to bot.log with line buffering.
try:
    if sys.stdout is None or not hasattr(sys.stdout, "write"):
        sys.stdout = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
    if sys.stderr is None or not hasattr(sys.stderr, "write"):
        sys.stderr = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
except Exception:
    pass


def log_event(msg: str):
    """Writes timestamped entry to bot.log and stdout."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] {msg}"
    try:
        print(formatted, flush=True)
    except Exception:
        pass
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def send_telegram_message(
    token: str,
    chat_id: Any,
    text: str,
    reply_markup: Optional[Dict[str, Any]] = None,
    parse_mode: str = "Markdown"
) -> bool:
    """Dispatches a message to Telegram with optional inline keyboard and markdown fallback."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        resp = requests.post(url, json=payload, timeout=12)
        if resp.status_code == 200:
            return True
        log_event(f"sendMessage failed (code {resp.status_code}): {resp.text}")
        # If Markdown entity parse error, retry with clean plain text
        if "parse" in resp.text.lower() or "bad request" in resp.text.lower():
            clean_text = text.replace("*", "").replace("`", "").replace("_", "")
            payload["text"] = clean_text
            payload.pop("parse_mode", None)
            retry_resp = requests.post(url, json=payload, timeout=12)
            return retry_resp.status_code == 200
        return False
    except Exception as e:
        log_event(f"Error sending message to {chat_id}: {e}")
        return False


def answer_callback_query(token: str, callback_query_id: str, text: Optional[str] = None):
    """Answers Telegram callback queries so buttons stop spinning."""
    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass


def format_interactive_stock_analysis(query: str, capital_inr: float = 5000.0, lang: str = "en") -> str:
    """
    Resolves any user input (full company name, typo, or ticker) to NSE symbol,
    and returns a localized analysis card in the user's chosen language (en, hi, or gu).
    """
    raw_query = query.replace("/CHECK", "").replace("/check", "").strip()
    if not raw_query:
        if lang == "hi":
            return "❌ कृपया किसी शेयर या कंपनी का नाम लिखें (जैसे `Tata Motors`, `SBIN`, `GOLDBEES`)।"
        elif lang == "gu":
            return "❌ કૃપા કરીને કોઈપણ શેર અથવા કંપનીનું નામ લખો (જેમ કે `Tata Motors`, `SBIN`, `GOLDBEES`)."
        else:
            return "❌ Please type a stock or company name (e.g. `Tata Motors`, `SBIN`, `GOLDBEES`)."

    # Smart Name / Symbol Resolver
    sym, company_name = resolve_stock_symbol(raw_query)

    if not sym:
        return localization.format_symbol_not_found(raw_query, lang=lang)

    clean_sym = sym.replace(".NS", "").replace(".BO", "")
    display_title = company_name if company_name else clean_sym

    shield = TradeShield(capital_inr=capital_inr)
    df = fetch_stock_data(sym, period="6mo")

    if df is None or len(df) < 30:
        if lang == "hi":
            return f"❌ *{display_title}* (`{sym}`) का चार्ट डेटा लोड नहीं हो सका। यह शेयर नया या कम लिक्विडिटी वाला हो सकता है।"
        elif lang == "gu":
            return f"❌ *{display_title}* (`{sym}`) નો ચાર્ટ ડેટા લોડ થઈ શક્યો નથી. આ શેર નવો અથવા ઓછી લિક્વિડિટી વાળો હોઈ શકે છે."
        else:
            return f"❌ Could not load price chart for *{display_title}* (`{sym}`). It may be newly listed or illiquid."

    signal = analyze_stock_signal(sym, df, shield)
    if not signal:
        if lang == "hi":
            return f"❌ *{display_title}* का सुरक्षित मूल्यांकन करने के लिए पर्याप्त तकनीकी डेटा नहीं मिला।"
        elif lang == "gu":
            return f"❌ *{display_title}* નું સુરક્ષિત મૂલ્યાંકન કરવા માટે પૂરતો ડેટા મળ્યો નથી."
        else:
            return f"❌ Insufficient historical data to evaluate *{display_title}* safely."

    sh = signal["shield"]
    price = signal["entry_price"]
    score = signal["confidence_score"]
    rsi = signal["rsi"]
    vol = signal["volume_surge"]
    reasons = signal.get("reasons", [])

    return localization.format_stock_analysis_card(
        display_title=display_title,
        clean_sym=clean_sym,
        price=price,
        score=score,
        rsi=rsi,
        vol=vol,
        sh=sh,
        reasons=reasons,
        lang=lang
    )


def background_daily_scheduler():
    """
    Autonomous, state-aware background scheduler.
    Triggers market predictions report for weekdays (Monday - Friday):
      - Morning Scan: 9:00 AM to 3:30 PM (if not yet delivered today)
      - Evening Scan: 4:00 PM onwards (if not yet delivered today)
    Skips weekends (Saturday & Sunday).
    If the laptop was asleep at 9:00 AM or 4:00 PM, it automatically catches up
    and sends the report immediately upon wake!
    """
    log_event("Resilient TradeShield Schedule Monitor started (Catch-Up Aware 9 AM & 4 PM Weekdays)")

    while True:
        try:
            now = datetime.now()
            weekday = now.weekday()  # 0=Monday, 4=Friday, 5=Sat, 6=Sun
            today_str = now.strftime("%Y-%m-%d")

            if weekday < 5:  # Monday to Friday only
                state = load_schedule_state()

                # Morning slot: from 09:00 AM up to 15:30 (3:30 PM market hours)
                if (now.hour > 9 or (now.hour == 9 and now.minute >= 0)) and (now.hour < 15 or (now.hour == 15 and now.minute <= 30)):
                    if state.get("last_morning_date") != today_str:
                        log_event(f"🔔 Generating 9:00 AM Morning Market Scan & Dispatch for {today_str}...")
                        state["last_morning_date"] = today_str
                        save_schedule_state(state)
                        daily_tracker.generate_daily_prediction_report(capital_inr=config.DEFAULT_CAPITAL_INR)
                        log_event(f"✅ 9:00 AM Morning Market Update successfully dispatched for {today_str}!")

                # Evening slot: from 16:00 (4:00 PM) onwards
                elif now.hour >= 16:
                    if state.get("last_evening_date") != today_str:
                        log_event(f"🔔 Generating 4:00 PM Market Close Scan & Dispatch for {today_str}...")
                        state["last_evening_date"] = today_str
                        save_schedule_state(state)
                        daily_tracker.generate_daily_prediction_report(capital_inr=config.DEFAULT_CAPITAL_INR)
                        log_event(f"✅ 4:00 PM Market Update successfully dispatched for {today_str}!")

        except Exception as e:
            log_event(f"Schedule monitor error: {e}")

        time.sleep(30)


def run_telegram_bot_listener():
    """
    Main loop listening for messages and inline button clicks on Telegram.
    Provides instant multilingual stock analysis and language configuration.
    """
    enforce_single_instance()

    token = config.TELEGRAM_BOT_TOKEN
    if not token:
        log_event("ERROR: Telegram bot token not configured in .env!")
        return

    # Start background scheduler thread for 9 AM & 4 PM weekday updates
    sched_thread = threading.Thread(target=background_daily_scheduler, daemon=True)
    sched_thread.start()

    log_event("TradeShield Multilingual Telegram Listener is RUNNING...")
    log_event("Languages supported: English (en), Hindi (hi), Gujarati (gu)")
    offset = 0

    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={offset}&timeout=15"
            resp = requests.get(url, timeout=20)
            if resp.status_code != 200:
                time.sleep(2)
                continue

            data = resp.json()
            if not data.get("ok"):
                time.sleep(2)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                # 1. Handle Inline Button Clicks (Language Selection)
                callback_query = update.get("callback_query")
                if callback_query:
                    cb_id = callback_query.get("id")
                    from_user = callback_query.get("from", {})
                    chat_id = from_user.get("id")
                    cb_data = callback_query.get("data", "")

                    log_event(f"Button Click from {from_user.get('first_name')} ({chat_id}): '{cb_data}'")

                    if cb_data.startswith("set_lang_"):
                        chosen_lang = cb_data.replace("set_lang_", "").strip().lower()
                        user_info = {
                            "first_name": from_user.get("first_name", ""),
                            "last_name": from_user.get("last_name", ""),
                            "username": from_user.get("username", "")
                        }
                        user_preferences.set_user_language(chat_id, chosen_lang, user_info)
                        answer_callback_query(token, cb_id, text="Language Updated!")
                        confirm_text = localization.get_language_set_confirmation(chosen_lang)
                        send_telegram_message(token, chat_id, confirm_text)
                        continue

                # 2. Handle Text Messages
                msg = update.get("message")
                if not msg or "text" not in msg:
                    continue

                chat_id = msg["chat"]["id"]
                user_text = msg["text"].strip()
                from_user = msg.get("from", {})
                sender_name = from_user.get("first_name", "Trader")

                # Register / update user metadata
                user_info = {
                    "first_name": from_user.get("first_name", ""),
                    "last_name": from_user.get("last_name", ""),
                    "username": from_user.get("username", "")
                }
                curr_lang = user_preferences.get_user_language(chat_id)

                log_event(f"Query from {sender_name} ({chat_id}) [Lang: {curr_lang}]: '{user_text}'")

                # Command: Language change prompt
                if user_text.lower() in ["/language", "/lang", "language", "lang", "भाषा", "ભાષા"]:
                    prompt_text = localization.get_language_prompt_text()
                    kbd = localization.get_language_inline_keyboard()
                    send_telegram_message(token, chat_id, prompt_text, reply_markup=kbd)
                    continue

                # Quick Direct Commands for Language Switching
                if user_text.lower() in ["/english", "/en"]:
                    user_preferences.set_user_language(chat_id, "en", user_info)
                    send_telegram_message(token, chat_id, localization.get_language_set_confirmation("en"))
                    continue
                if user_text.lower() in ["/hindi", "/hi"]:
                    user_preferences.set_user_language(chat_id, "hi", user_info)
                    send_telegram_message(token, chat_id, localization.get_language_set_confirmation("hi"))
                    continue
                if user_text.lower() in ["/gujarati", "/gu"]:
                    user_preferences.set_user_language(chat_id, "gu", user_info)
                    send_telegram_message(token, chat_id, localization.get_language_set_confirmation("gu"))
                    continue

                # Command: Start / Help / Greeting
                if user_text.startswith("/start") or user_text.lower() in ["hi", "hello", "help", "/help", "kem cho"]:
                    welcome_text = localization.get_welcome_message(sender_name=sender_name, lang=curr_lang)
                    kbd = localization.get_language_inline_keyboard()
                    send_telegram_message(token, chat_id, welcome_text, reply_markup=kbd)
                    continue

                # Command: Trigger instant market predictions scan
                if user_text.lower() in ["/scan", "/today", "/update", "update"]:
                    status_text = "🔍 Scanning live market for today's best setups..."
                    if curr_lang == "hi":
                        status_text = "🔍 आज के सर्वोत्तम ट्रेड्स के लिए मार्केट स्कैन किया जा रहा है..."
                    elif curr_lang == "gu":
                        status_text = "🔍 આજના શ્રેષ્ઠ સેટઅપ્સ માટે માર્કેટ સ્કેન થઈ રહ્યું છે..."
                    send_telegram_message(token, chat_id, status_text)
                    daily_tracker.generate_daily_prediction_report(capital_inr=config.DEFAULT_CAPITAL_INR)
                    continue

                # Normal Stock Analysis Query
                analyzing_msg = localization.get_analyzing_message(user_text, lang=curr_lang)
                send_telegram_message(token, chat_id, analyzing_msg)

                analysis_card = format_interactive_stock_analysis(
                    query=user_text,
                    capital_inr=config.DEFAULT_CAPITAL_INR,
                    lang=curr_lang
                )
                send_telegram_message(token, chat_id, analysis_card)

        except requests.exceptions.RequestException as re:
            log_event(f"Network error in listener: {re}")
            time.sleep(3)
        except Exception as e:
            log_event(f"Listener error: {e}")
            time.sleep(2)


if __name__ == "__main__":
    run_telegram_bot_listener()
