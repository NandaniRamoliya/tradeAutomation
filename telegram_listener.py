import time
import threading
from datetime import datetime
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


def send_telegram_message(
    token: str,
    chat_id: Any,
    text: str,
    reply_markup: Optional[Dict[str, Any]] = None,
    parse_mode: str = "Markdown"
) -> bool:
    """Dispatches a message to Telegram with optional inline keyboard."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")
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
            return f"❌ *{display_title}* (`{sym}`) का चार्ट डेटा लोड नहीं हो सका। यह शेयर नया हो सकता है।"
        elif lang == "gu":
            return f"❌ *{display_title}* (`{sym}`) નો ચાર્ટ ડેટા લોડ થઈ શક્યો નથી. આ શેર નવો હોઈ શકે છે."
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
    Autonomous background thread that checks time every 30 seconds.
    Triggers market predictions report at:
      - 09:00 AM (Monday - Friday)
      - 04:00 PM (Monday - Friday)
    Skips weekends (Saturday & Sunday).
    """
    print("⏰ Autonomous TradeShield Schedule Monitor started (9:00 AM & 4:00 PM Weekdays)...")
    last_triggered_slot = ""

    while True:
        try:
            now = datetime.now()
            # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
            weekday = now.weekday()
            current_date_str = now.strftime("%Y-%m-%d")
            hour = now.hour
            minute = now.minute

            if weekday < 5:  # Monday to Friday only
                # Morning Slot (9:00 AM - 9:05 AM window)
                if hour == 9 and 0 <= minute <= 5:
                    slot_key = f"{current_date_str}_0900"
                    if slot_key != last_triggered_slot:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔔 Triggering 9:00 AM Morning Market Scan & Dispatch...")
                        last_triggered_slot = slot_key
                        daily_tracker.generate_daily_prediction_report(capital_inr=config.DEFAULT_CAPITAL_INR)
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 9:00 AM Morning Market Update successfully dispatched!")

                # Evening Slot (16:00 / 4:00 PM - 16:05 window)
                elif hour == 16 and 0 <= minute <= 5:
                    slot_key = f"{current_date_str}_1600"
                    if slot_key != last_triggered_slot:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔔 Triggering 4:00 PM Market Close Scan & Dispatch...")
                        last_triggered_slot = slot_key
                        daily_tracker.generate_daily_prediction_report(capital_inr=config.DEFAULT_CAPITAL_INR)
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 4:00 PM Market Update successfully dispatched!")

        except Exception as e:
            print(f"Schedule monitor error: {e}")

        time.sleep(30)


def run_telegram_bot_listener():
    """
    Main loop listening for messages and inline button clicks on Telegram.
    Provides instant multilingual stock analysis and language configuration.
    """
    token = config.TELEGRAM_BOT_TOKEN
    if not token:
        print("❌ Telegram bot token not configured in .env!")
        return

    # Start background scheduler thread for 9 AM & 4 PM weekday updates
    sched_thread = threading.Thread(target=background_daily_scheduler, daemon=True)
    sched_thread.start()

    print("🤖 TradeShield Multilingual Telegram Listener is RUNNING...")
    print("Supports: English (en), Hindi (hi), Gujarati (gu)")
    offset = 0

    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={offset}&timeout=15"
            resp = requests.get(url, timeout=20)
            if resp.status_code != 200:
                time.sleep(3)
                continue

            data = resp.json()
            if not data.get("ok"):
                time.sleep(3)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                # 1. Handle Inline Button Clicks (Language Selection)
                callback_query = update.get("callback_query")
                if callback_query:
                    cb_id = callback_query["id"]
                    from_user = callback_query.get("from", {})
                    chat_id = from_user.get("id")
                    cb_data = callback_query.get("data", "")

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

                print(f"[{datetime.now().strftime('%H:%M:%S')}] Query from {sender_name} ({chat_id}) [Lang: {curr_lang}]: '{user_text}'")

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
                    # Show welcome message in current language and include language picker buttons
                    welcome_text = localization.get_welcome_message(sender_name=sender_name, lang=curr_lang)
                    kbd = localization.get_language_inline_keyboard()
                    send_telegram_message(token, chat_id, welcome_text, reply_markup=kbd)
                    continue

                # Command: Trigger instant market predictions test
                if user_text.lower() in ["/scan", "/today", "/update", "update"]:
                    send_telegram_message(token, chat_id, "🔍 Scanning live market for today's best setups...")
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

        except requests.exceptions.RequestException:
            time.sleep(5)
        except Exception as e:
            print(f"Listener loop error: {e}")
            time.sleep(3)


if __name__ == "__main__":
    run_telegram_bot_listener()
