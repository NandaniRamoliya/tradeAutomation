import pandas as pd
import numpy as np


def flatten_yfinance_columns(df: pd.DataFrame, ticker: str = "") -> pd.DataFrame:
    """Flatten MultiIndex columns if returned by yfinance."""
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        # Handle cases like ('Close', 'INFY.NS') or ('Price', 'Close')
        new_cols = []
        for col in df.columns:
            if isinstance(col, tuple):
                # Pick the standard OHLCV name
                name = col[0]
                if name.lower() not in ["open", "high", "low", "close", "adj close", "volume"] and len(col) > 1:
                    name = col[1] if col[1].lower() in ["open", "high", "low", "close", "adj close", "volume"] else col[0]
                new_cols.append(name)
            else:
                new_cols.append(col)
        df.columns = new_cols
    # Ensure standard title case
    rename_dict = {
        "open": "Open", "high": "High", "low": "Low", "close": "Close",
        "volume": "Volume", "adj close": "Adj Close"
    }
    df = df.rename(columns={c: rename_dict[c.lower()] for c in df.columns if c.lower() in rename_dict})
    return df


def calculate_ema(series: pd.Series, span: int) -> pd.Series:
    """Calculate Exponential Moving Average."""
    return series.ewm(span=span, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index (RSI)."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0.0)).copy()
    loss = (-delta.where(delta < 0, 0.0)).copy()

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # Wilder's Smoothing
    for i in range(period, len(series)):
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Average True Range (ATR)."""
    high = df["High"]
    low = df["Low"]
    close_prev = df["Close"].shift(1)

    tr1 = high - low
    tr2 = (high - close_prev).abs()
    tr3 = (low - close_prev).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period, min_periods=period).mean()
    return atr


def get_market_hours_volume_scaling() -> float:
    """Returns scaling factor for volume during live NSE market hours (9:15 AM - 3:30 PM)."""
    from datetime import datetime
    now = datetime.now()
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)

    if market_open <= now <= market_close:
        elapsed = (now - market_open).total_seconds()
        total_day = (market_close - market_open).total_seconds()
        frac = elapsed / total_day
        return max(frac, 0.20)  # At least 20%
    return 1.0


def enrich_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches candle DataFrame with EMA 9/21/50/200, RSI, ATR,
    Volume SMA, and Breakout markers.
    """
    df = flatten_yfinance_columns(df)
    if len(df) < 50:
        return df

    # EMAs
    df["EMA_9"] = calculate_ema(df["Close"], 9)
    df["EMA_21"] = calculate_ema(df["Close"], 21)
    df["EMA_50"] = calculate_ema(df["Close"], 50)
    if len(df) >= 200:
        df["EMA_200"] = calculate_ema(df["Close"], 200)
    else:
        df["EMA_200"] = df["EMA_50"]  # fallback if less data available

    # RSI
    df["RSI"] = calculate_rsi(df["Close"], 14)

    # ATR
    df["ATR"] = calculate_atr(df, 14)

    # Volume Analysis
    df["Volume_SMA20"] = df["Volume"].rolling(window=20).mean()
    df["Volume_Surge_Ratio"] = df["Volume"] / (df["Volume_SMA20"] + 1e-9)
    # Adjust latest bar if during market hours
    scale = get_market_hours_volume_scaling()
    if scale < 1.0 and len(df) > 0:
        df.iloc[-1, df.columns.get_loc("Volume_Surge_Ratio")] = float(df.iloc[-1]["Volume_Surge_Ratio"]) / scale

    # Price action metrics
    df["5D_High"] = df["High"].shift(1).rolling(window=5).max()
    df["20D_High"] = df["High"].shift(1).rolling(window=20).max()
    df["5D_Low"] = df["Low"].shift(1).rolling(window=5).min()

    # Candle characteristics
    df["Body_Pct"] = ((df["Close"] - df["Open"]).abs()) / (df["High"] - df["Low"] + 1e-9)
    df["Is_Bullish"] = df["Close"] > df["Open"]

    return df

