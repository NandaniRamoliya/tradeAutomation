from typing import Dict, Any, List, Optional
import pandas as pd
from shield import TradeShield
from data_fetcher import fetch_stock_data, load_stock_universe


def analyze_stock_signal(symbol: str, df: pd.DataFrame, shield: TradeShield) -> Optional[Dict[str, Any]]:
    """
    Analyzes the latest candle and historical metrics of a stock,
    calculates confidence score, runs through Shield risk validation,
    and returns a structured signal card.
    """
    if df is None or len(df) < 50:
        return None

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    close = float(latest["Close"])
    open_p = float(latest["Open"])
    high = float(latest["High"])
    low = float(latest["Low"])
    volume = float(latest["Volume"])
    vol_surge = float(latest.get("Volume_Surge_Ratio", 1.0))
    rsi = float(latest.get("RSI", 50.0))
    ema_9 = float(latest.get("EMA_9", close))
    ema_21 = float(latest.get("EMA_21", close))
    ema_50 = float(latest.get("EMA_50", close))
    ema_200 = float(latest.get("EMA_200", close))
    atr = float(latest.get("ATR", close * 0.02))
    five_day_high = float(latest.get("5D_High", high))
    recent_low = float(latest.get("5D_Low", low))

    # --- Confidence Scoring (0 - 100) ---
    score = 0
    reasons = []

    # 1. Trend & Moving Average Confluence (up to 30 points)
    if close > ema_50 and close > ema_200:
        score += 15
        reasons.append("Above 50 & 200 EMA (Macro Bullish)")
    elif close > ema_50:
        score += 8
        reasons.append("Above 50 EMA")

    if ema_9 > ema_21 and close > ema_9:
        score += 15
        reasons.append("9 EMA > 21 EMA Bullish Crossover")

    # 2. Volume Surge (up to 25 points)
    if vol_surge >= 2.0:
        score += 25
        reasons.append(f"Institutional Volume Surge ({vol_surge:.1f}x 20-day avg)")
    elif vol_surge >= 1.3:
        score += 15
        reasons.append(f"Above Average Volume ({vol_surge:.1f}x 20-day avg)")
    elif vol_surge < 0.8:
        reasons.append("Low Volume warning")

    # 3. RSI Momentum (up to 20 points)
    if 55.0 <= rsi <= 68.0:
        score += 20
        reasons.append(f"RSI in Prime Momentum Zone ({rsi:.1f})")
    elif 50.0 <= rsi < 55.0:
        score += 10
        reasons.append(f"RSI Bullish Baseline ({rsi:.1f})")
    elif rsi > 70.0:
        reasons.append(f"RSI Overheated ({rsi:.1f})")

    # 4. Breakout & Price Action (up to 25 points)
    is_5d_breakout = close > five_day_high
    candle_range = high - low + 1e-9
    close_near_high = (high - close) / candle_range <= 0.30  # Closed in upper 30% of day's range

    if is_5d_breakout:
        score += 15
        reasons.append("5-Day High Breakout")

    if close > open_p and close_near_high:
        score += 10
        reasons.append("Strong Bullish Close near day's high")

    # --- Evaluate with TradeShield ---
    shield_eval = shield.evaluate_risk(
        symbol=symbol,
        current_price=close,
        atr=atr,
        rsi=rsi,
        ema_50=ema_50,
        ema_200=ema_200,
        volume_surge=vol_surge,
        recent_low=recent_low
    )

    action = "WAIT / NO SIGNAL"
    if score >= 70 and shield_eval["is_approved"]:
        action = "STRONG BUY"
    elif score >= 55 and shield_eval["is_approved"]:
        action = "MODERATE BUY"
    elif not shield_eval["is_approved"]:
        action = "REJECTED BY SHIELD"

    signal_card = {
        "symbol": symbol,
        "action": action,
        "confidence_score": score,
        "entry_price": close,
        "rsi": round(rsi, 1),
        "volume_surge": round(vol_surge, 2),
        "reasons": reasons,
        "shield": shield_eval
    }

    return signal_card


def scan_market(
    symbols: Optional[List[str]] = None,
    shield: Optional[TradeShield] = None,
    min_confidence: int = 55
) -> List[Dict[str, Any]]:
    """
    Scans a list of stocks and returns actionable signals filtered and approved by TradeShield.
    """
    if symbols is None:
        symbols = load_stock_universe()
    if shield is None:
        shield = TradeShield()

    approved_signals = []

    for sym in symbols:
        df = fetch_stock_data(sym)
        if df is None:
            continue
        signal = analyze_stock_signal(sym, df, shield)
        if signal and signal["shield"]["is_approved"] and signal["confidence_score"] >= min_confidence:
            approved_signals.append(signal)

    # Sort descending by confidence score
    approved_signals.sort(key=lambda x: x["confidence_score"], reverse=True)
    return approved_signals

