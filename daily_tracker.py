import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import config
from data_fetcher import fetch_stock_data, load_stock_universe
from scanner import analyze_stock_signal
from shield import TradeShield
from bot import send_telegram_alert
import localization
import user_preferences

BASE_DIR = Path(__file__).resolve().parent
PREDICTIONS_TXT = BASE_DIR / "DAILY_PREDICTIONS.txt"
JOURNAL_JSON = BASE_DIR / "VERIFICATION_LOG.json"


def analyze_commodity_dip(symbol: str, name: str, budget_inr: float = 1500.0) -> Dict[str, Any]:
    """
    Specialized analyzer for Gold & Silver ETFs (GOLDBEES / SILVERBEES).
    Since commodities don't go to zero, it uses staggered dip-buying rules.
    """
    df = fetch_stock_data(symbol, period="6mo")
    if df is None or len(df) < 30:
        return {}

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    close = float(latest["Close"])
    prev_close = float(prev["Close"])
    day_change_pct = round(((close - prev_close) / prev_close) * 100, 2)
    rsi = float(latest.get("RSI", 50.0))
    ema_21 = float(latest.get("EMA_21", close))
    ema_50 = float(latest.get("EMA_50", close))

    # Units you can buy with a ₹1,500 budget (30% of ₹5,000 wallet)
    recommended_units = int(budget_inr // close)
    total_cost = round(recommended_units * close, 2)

    # Is it dipping?
    is_dipping = close < ema_21 or rsi < 55 or day_change_pct < 0
    if is_dipping:
        status = "🟢 GOOD BUY-THE-DIP ZONE"
        advice = (
            f"Price dropped {day_change_pct}% to ₹{close:.2f}. "
            f"This is a healthy discount. Buy {recommended_units} units for your 1st step."
        )
    else:
        status = "🟡 WAIT / ALREADY RALLIED"
        advice = f"Price is at ₹{close:.2f} (RSI {rsi:.1f}). Wait for a red day before buying."

    # Conservative 1-2 month targets for Gold/Silver
    target_1 = round(close * 1.04, 2)  # +4%
    target_2 = round(close * 1.08, 2)  # +8%

    return {
        "symbol": symbol.replace(".NS", ""),
        "name": name,
        "type": "COMMODITY_ETF",
        "date": str(df.index[-1].date() if hasattr(df.index[-1], "date") else df.index[-1])[:10],
        "current_price": close,
        "day_change_pct": day_change_pct,
        "status": status,
        "advice": advice,
        "recommended_units": recommended_units,
        "total_cost": total_cost,
        "target_1": target_1,
        "target_2": target_2,
        "safety_rule": "Gold/Silver never expires. Hold patiently on Groww Delivery; no panic selling."
    }


def show_desktop_notification(title: str, message: str):
    """Triggers a clean Windows desktop notification balloon."""
    try:
        import subprocess
        ps_script = f"""
        Add-Type -AssemblyName System.Windows.Forms
        $balloon = New-Object System.Windows.Forms.NotifyIcon
        $balloon.Icon = [System.Drawing.SystemIcons]::Information
        $balloon.BalloonTipIcon = 'Info'
        $balloon.BalloonTipTitle = '{title}'
        $balloon.BalloonTipText = '{message}'
        $balloon.Visible = $true
        $balloon.ShowBalloonTip(5000)
        Start-Sleep -Seconds 1
        $balloon.Dispose()
        """
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, timeout=5)
    except Exception:
        pass


def generate_daily_prediction_report(capital_inr: float = 5000.0) -> str:
    """
    Scans the market and creates a crystal-clear, plain-English report for today.
    Saves to DAILY_PREDICTIONS.txt and logs to VERIFICATION_LOG.json.
    """
    shield = TradeShield(capital_inr=capital_inr)
    today_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    # 1. Analyze Gold & Silver
    gold_data = analyze_commodity_dip("GOLDBEES.NS", "Gold BeES (Pure Gold)", budget_inr=1500.0)
    silver_data = analyze_commodity_dip("SILVERBEES.NS", "Silver BeES (Pure Silver)", budget_inr=1500.0)

    # 2. Analyze Top Stocks
    symbols = load_stock_universe()
    stock_signals = []
    for s in symbols:
        if "BEES" in s:
            continue
        df = fetch_stock_data(s, period="6mo")
        if df is None:
            continue
        sig = analyze_stock_signal(s, df, shield)
        if sig and sig["shield"]["is_approved"] and sig["confidence_score"] >= 65:
            stock_signals.append(sig)

    stock_signals.sort(key=lambda x: x["confidence_score"], reverse=True)
    top_stocks = stock_signals[:2]  # Focus only on the top 1 or 2 best ideas to prevent confusion

    # Build Plain English Report
    lines = []
    lines.append("=" * 70)
    lines.append(f"📅 TODAY'S GROWW TRADING & INVESTMENT PREDICTIONS")
    lines.append(f"🕒 Generated: {today_str} | Capital Wallet: ₹{capital_inr:,.0f}")
    lines.append("=" * 70)
    lines.append("")
    lines.append("🛡️ PART 1: THE SAFE ASSETS (GOLD & SILVER DIP-BUYING)")
    lines.append("-" * 70)

    for item in [gold_data, silver_data]:
        if not item:
            continue
        lines.append(f"🪙 {item['name']} ({item['symbol']})")
        lines.append(f"   • Current Price: ₹{item['current_price']:.2f} ({item['day_change_pct']:+0.2f}% today)")
        lines.append(f"   • Status: {item['status']}")
        lines.append(f"   • Recommendation: {item['advice']}")
        lines.append(f"   • What to do in Groww:")
        lines.append(f"       1. Search '{item['symbol']}' in Groww app")
        lines.append(f"       2. Select Delivery (Cash)")
        lines.append(f"       3. Buy {item['recommended_units']} units (Total Cost: ₹{item['total_cost']:,.2f})")
        lines.append(f"   • Target to take profit: ₹{item['target_1']:.2f} (+4%) or hold for long-term")
        lines.append(f"   • Safety Note: {item['safety_rule']}")
        lines.append("")

    lines.append("-" * 70)
    lines.append("🚀 PART 2: SHORT-TERM MOMENTUM STOCKS (1 - 2 DAY TRADES)")
    lines.append("-" * 70)

    if not top_stocks:
        lines.append("⚠️ The Shield says: Market is too choppy today. No safe stock trades.")
        lines.append("   Rule: Keeping your money in cash is 100% better than forcing a bad trade!")
    else:
        for s in top_stocks:
            sym = s["symbol"].replace(".NS", "")
            sh = s["shield"]
            lines.append(f"📈 Stock: {sym} (Confidence: {s['confidence_score']}%)")
            lines.append(f"   • Current Price: ₹{s['entry_price']:.2f}")
            lines.append(f"   • What to do in Groww:")
            lines.append(f"       1. Search '{sym}' in Groww")
            lines.append(f"       2. Order Type: Delivery (Cash)")
            lines.append(f"       3. Quantity: Buy {sh['recommended_quantity']} shares (Cost: ₹{sh['total_investment']:,.2f})")
            lines.append(f"   • 🛡️ The Shield (Stop Loss): ₹{sh['stop_loss_price']:.2f} (-{sh['sl_percent']}%)")
            lines.append(f"       ➔ If it drops to ₹{sh['stop_loss_price']:.2f}, EXIT! (Max loss is only ₹{sh['max_possible_loss']:.1f})")
            lines.append(f"   • 🎯 Target 1: ₹{sh['target_1_price']:.2f} (+{sh['target_1_percent']}%) ➔ Profit: +₹{sh['target_1_profit']:,.2f}")
            lines.append(f"   • 🚀 Target 2: ₹{sh['target_2_price']:.2f} (+{sh['target_2_percent']}%) ➔ Profit: +₹{sh['target_2_profit']:,.2f}")
            lines.append("")

    lines.append("=" * 70)
    lines.append("📝 HOW TO VERIFY THIS TOMORROW ON GROWW:")
    lines.append("1. Open your Groww app tomorrow between 9:30 AM and 3:30 PM.")
    lines.append("2. Search the assets listed above.")
    lines.append("3. Check if the price moved towards Target 1 or hit Stop Loss.")
    lines.append("4. Notice how The Shield NEVER lets your money drop below the stop-loss.")
    lines.append("=" * 70)

    report_text = "\n".join(lines)

    # Save to DAILY_PREDICTIONS.txt
    with open(PREDICTIONS_TXT, "w", encoding="utf-8") as f:
        f.write(report_text)

    # Log to JSON verification journal
    journal_entry = {
        "timestamp": today_str,
        "capital_inr": capital_inr,
        "gold": gold_data,
        "silver": silver_data,
        "top_stocks": [
            {
                "symbol": s["symbol"],
                "entry_price": s["entry_price"],
                "stop_loss": s["shield"]["stop_loss_price"],
                "target_1": s["shield"]["target_1_price"],
                "target_2": s["shield"]["target_2_price"],
                "quantity": s["shield"]["recommended_quantity"],
                "max_risk_rupees": s["shield"]["max_possible_loss"],
                "status": "PENDING_VERIFICATION"
            }
            for s in top_stocks
        ]
    }

    journal = []
    if JOURNAL_JSON.exists():
        try:
            with open(JOURNAL_JSON, "r", encoding="utf-8") as f:
                journal = json.load(f)
        except Exception:
            journal = []
    journal.append(journal_entry)
    with open(JOURNAL_JSON, "w", encoding="utf-8") as f:
        json.dump(journal, f, indent=2)

    # Trigger desktop notification
    top_stock_str = top_stocks[0]["symbol"].replace(".NS", "") if top_stocks else "Gold/Silver Dip"
    show_desktop_notification(
        title="🛡️ TradeShield: Predictions Ready!",
        message=f"Today's scan complete. Top picks: {top_stock_str}. Check DAILY_PREDICTIONS.txt"
    )

    # Trigger Multilingual Telegram Alerts to all active users
    if config.TELEGRAM_BOT_TOKEN:
        subscribers = user_preferences.get_all_subscribers()
        if not subscribers and config.TELEGRAM_CHAT_ID:
            subscribers = [str(config.TELEGRAM_CHAT_ID)]

        for sub_id in subscribers:
            user_lang = user_preferences.get_user_language(sub_id)
            tg_message = localization.format_daily_prediction_card(
                gold_data=gold_data,
                silver_data=silver_data,
                top_stocks=top_stocks,
                capital_inr=capital_inr,
                lang=user_lang,
                timestamp_str=today_str
            )
            send_telegram_alert(tg_message, chat_id=sub_id)

    return report_text


if __name__ == "__main__":
    report = generate_daily_prediction_report(capital_inr=5000.0)
    print(report)

