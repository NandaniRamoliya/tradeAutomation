import time
import requests
import config
from data_fetcher import fetch_stock_data
from scanner import analyze_stock_signal
from shield import TradeShield
from symbol_resolver import resolve_stock_symbol


def format_interactive_stock_analysis(query: str, capital_inr: float = 5000.0) -> str:
    """
    Resolves any user input (full company name, typo, or ticker) to NSE symbol,
    and generates a complete analysis for:
    1. Wants to invest now (New Buy)
    2. Already invested / holding this stock
    """
    raw_query = query.replace("/CHECK", "").replace("/check", "").strip()
    if not raw_query:
        return "❌ Please type a stock or company name (e.g. `Tata Motors`, `Omnitech`, `SBIN`)."

    # Smart Name / Symbol Resolver
    sym, company_name = resolve_stock_symbol(raw_query)

    if not sym:
        return (
            f"❌ *Could not find a stock matching '{raw_query}' on NSE/BSE.*\n\n"
            f"👉 *Tips:*\n"
            f"• You can type company names: `Tata Motors`, `Omnitech`, `State Bank`, `Reliance`\n"
            f"• Or exact tickers: `TATASTEEL`, `SBIN`, `IRFC`, `GOLDBEES`\n"
            f"• Please check spelling and try again!"
        )

    clean_sym = sym.replace(".NS", "").replace(".BO", "")
    display_title = company_name if company_name else clean_sym

    shield = TradeShield(capital_inr=capital_inr)
    df = fetch_stock_data(sym, period="6mo")

    if df is None or len(df) < 30:
        return f"❌ Could not load price chart for *{display_title}* (`{sym}`). It may be illiquid or newly listed."

    signal = analyze_stock_signal(sym, df, shield)
    if not signal:
        return f"❌ Insufficient historical data to evaluate *{display_title}* safely."

    sh = signal["shield"]
    price = signal["entry_price"]
    score = signal["confidence_score"]
    action = signal["action"]
    rsi = signal["rsi"]
    vol = signal["volume_surge"]
    sl = sh["stop_loss_price"]
    sl_pct = sh["sl_percent"]
    t1 = sh["target_1_price"]
    t1_pct = sh["target_1_percent"]
    t2 = sh["target_2_price"]
    t2_pct = sh["target_2_percent"]
    qty = sh["recommended_quantity"]

    reasons_text = "\n".join([f"  • {r}" for r in signal["reasons"][:3]])

    if sh["is_approved"]:
        status_header = f"🟢 *{display_title}* (`{clean_sym}`) — HIGH MOMENTUM ({score}% Score)"
        new_buyer_advice = (
            f"✅ *Safe to Enter in Groww (Delivery)*\n"
            f"• Recommended Buy Price: Around *₹{price:.2f}*\n"
            f"• Recommended Quantity: *{qty} shares* (Cost: ₹{sh['total_investment']:,.0f})\n"
            f"• 🛡️ *Shield Stop-Loss:* ₹{sl:.2f} (-{sl_pct}% | Max risk ₹{sh['max_possible_loss']:.1f})\n"
            f"• 🎯 *Target 1:* ₹{t1:.2f} (+{t1_pct}%) ➔ Profit: +₹{sh['target_1_profit']:,.0f}\n"
            f"• 🚀 *Target 2:* ₹{t2:.2f} (+{t2_pct}%) ➔ Profit: +₹{sh['target_2_profit']:,.0f}"
        )
        holding_advice = (
            f"📈 *Good Trend — Safe to HOLD*\n"
            f"• If you bought lower, the trend is strong. Let it run towards *₹{t1:.2f}*.\n"
            f"• *Action:* Move your stop-loss up to *₹{sl:.2f}* so you lock in your profit!"
        )
    else:
        status_header = f"⚠️ *{display_title}* (`{clean_sym}`) — CAUTION / NOT APPROVED"
        rejection_notes = "\n".join([f"  ⚠️ {r}" for r in sh["rejection_reasons"][:2]])
        new_buyer_advice = (
            f"🚫 *DO NOT BUY NOW (High Risk)*\n"
            f"{rejection_notes}\n"
            f"• *Advice:* Wait for a better pullback or volume breakout before entering."
        )
        holding_advice = (
            f"🛡️ *If you are already holding:*\n"
            f"• Stock is showing technical weakness or downtrend.\n"
            f"• If it drops below *₹{sl:.2f}*, cut losses or exit to protect your cash.\n"
            f"• Do NOT average down a falling stock."
        )

    msg = (
        f"{status_header}\n"
        f"💵 *Current Price:* ₹{price:.2f} (RSI: {rsi:.1f} | Vol: {vol:.1f}x)\n"
        f"--------------------------------------\n"
        f"👉 *CASE 1: IF YOU WANT TO BUY NOW*\n"
        f"{new_buyer_advice}\n"
        f"--------------------------------------\n"
        f"👉 *CASE 2: IF YOU ALREADY OWN IT*\n"
        f"{holding_advice}\n"
        f"--------------------------------------\n"
        f"📊 *Key Signals:*\n{reasons_text}\n\n"
        f"💡 *Remember:* Always trade in Cash Delivery. Keep your stop-loss strict!"
    )
    return msg


def run_telegram_bot_listener():
    """
    Listens for incoming messages from users on Telegram.
    When a user types a stock symbol, the bot instantly replies!
    """
    token = config.TELEGRAM_BOT_TOKEN
    if not token:
        print("Telegram bot token not configured in .env!")
        return

    print("🤖 TradeShield Telegram Interactive Listener is RUNNING...")
    print("Users can now send any stock name (e.g. TATASTEEL, SBIN) to the bot!")
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
                msg = update.get("message")
                if not msg or "text" not in msg:
                    continue

                chat_id = msg["chat"]["id"]
                user_text = msg["text"].strip()
                sender_name = msg.get("from", {}).get("first_name", "Trader")

                print(f"Received query from {sender_name} ({chat_id}): '{user_text}'")

                if user_text.startswith("/start") or user_text.lower() in ["hi", "hello", "help", "/help"]:
                    welcome_reply = (
                        f"👋 Hello {sender_name}!\n\n"
                        f"I am your *TradeShield Assistant* 🛡️\n\n"
                        f"Just send me **any NSE stock name**, and I will instantly tell you:\n"
                        f"1. Whether it is safe to **BUY NOW**\n"
                        f"2. What to do if you **ALREADY OWN IT** (Hold/Sell targets)\n\n"
                        f"👉 Try typing any of these now:\n"
                        f"• `TATASTEEL`\n"
                        f"• `SBIN`\n"
                        f"• `IRFC`\n"
                        f"• `PNB`\n"
                        f"• `GOLDBEES`\n"
                        f"• `INFY`"
                    )
                    send_reply(token, chat_id, welcome_reply)
                else:
                    # Treat the text as a stock query
                    send_reply(token, chat_id, f"🔍 Analyzing *{user_text.upper()}* with The Shield... Please wait 3 seconds.")
                    reply = format_interactive_stock_analysis(user_text)
                    send_reply(token, chat_id, reply)

        except requests.exceptions.RequestException:
            time.sleep(5)
        except Exception as e:
            print(f"Listener error: {e}")
            time.sleep(3)


def send_reply(token: str, chat_id: int, text: str):
    """Sends a message back to Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=8)
    except Exception as e:
        print(f"Send reply error: {e}")


if __name__ == "__main__":
    run_telegram_bot_listener()

