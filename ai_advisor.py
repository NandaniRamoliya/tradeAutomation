from typing import Dict, Any


def generate_trade_guidance(signal: Dict[str, Any], capital_inr: float) -> str:
    """
    Generates a human-friendly step-by-step trading guide for the user in Groww.
    """
    sym = signal["symbol"].replace(".NS", "")
    entry = signal["entry_price"]
    score = signal["confidence_score"]
    shield = signal["shield"]

    sl = shield["stop_loss_price"]
    sl_pct = shield["sl_percent"]
    t1 = shield["target_1_price"]
    t1_pct = shield["target_1_percent"]
    t2 = shield["target_2_price"]
    t2_pct = shield["target_2_percent"]
    qty = shield["recommended_quantity"]
    investment = shield["total_investment"]
    max_loss = shield["max_possible_loss"]
    profit_t1 = shield["target_1_profit"]
    reasons = " • " + "\n • ".join(signal["reasons"])

    guidance = f"""
================================================================================
🎯 TRADE TRIGGER: {sym} (Confidence: {score}% - {signal['action']})
================================================================================
📍 STEP 1: HOW TO EXECUTE IN GROWW
   • Open your Groww app and search for: "{sym}"
   • Order Type: Delivery (Cash Equity)
   • Action: BUY
   • Recommended Quantity: {qty} shares
   • Total Investment: ₹{investment:,.2f} (from your ₹{capital_inr:,.2f} wallet)

🛡️ STEP 2: YOUR SHIELD (CAPITAL PROTECTION)
   • Stop-Loss Level: ₹{sl:,.2f} (-{sl_pct}%)
   • Maximum Rupee Loss: ₹{max_loss:,.2f} ({shield['max_loss_pct_of_capital']}% of your account)
   • Golden Rule: If the stock drops to ₹{sl:,.2f}, exit immediately. Never hold and hope!

🚀 STEP 3: WHERE TO SELL (1 - 2 DAY TARGETS)
   • Target 1 (Quick exit): ₹{t1:,.2f} (+{t1_pct}%) ➔ Potential Profit: ₹{profit_t1:,.2f}
   • Target 2 (Runner): ₹{t2:,.2f} (+{t2_pct}%) ➔ Potential Profit: ₹{shield['target_2_profit']:,.2f}
   • Strategy: When Target 1 hits, sell half your shares to lock in profits, then move your Stop-Loss to your entry price!

📊 WHY THE DATA FLAGGED THIS:
{reasons}
================================================================================
"""
    return guidance.strip()


def get_beginner_shield_tip() -> str:
    """Returns rotating risk management tips."""
    tips = [
        "🛡️ SHIELD TIP: Never trade Options or Intraday F&O as a beginner. In Delivery (Cash), your shares are yours and cannot become zero overnight.",
        "🛡️ SHIELD TIP: 8% returns in 2 days happen during big breakouts, but taking 2.5% - 4% gains consistently with strict 1.5% stop-losses is how real wealth compounds.",
        "🛡️ SHIELD TIP: Never average down a losing stock. Cut losses quickly when the Shield Stop-Loss triggers, and let your winners run to Target 1.",
        "🛡️ SHIELD TIP: Always check the trade size. If you cannot afford the stop loss in Rupees, do not take the trade."
    ]
    import random
    return random.choice(tips)

