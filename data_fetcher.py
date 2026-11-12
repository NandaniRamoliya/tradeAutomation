import json
from pathlib import Path
from typing import Dict, List, Optional
import yfinance as yf
import pandas as pd
import config
from indicators import enrich_technical_indicators


def load_stock_universe(file_path: Optional[Path] = None) -> List[str]:
    """Loads curated list of symbols from JSON."""
    path = file_path or config.STOCKS_UNIVERSE_PATH
    if not path.exists():
        # Fallback list if file not found
        return ["TATASTEEL.NS", "BEL.NS", "BHEL.NS", "COALINDIA.NS", "FEDERALBNK.NS", "INFY.NS"]
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("symbols", [])


def fetch_stock_data(symbol: str, period: str = "6mo", interval: str = "1d") -> Optional[pd.DataFrame]:
    """
    Fetches historical data for a single symbol and enriches with technical indicators.
    """
    try:
        # Standardize symbol for NSE if .NS missing and not an index
        ticker = symbol.upper()
        if not (ticker.endswith(".NS") or ticker.endswith(".BO") or ticker.startswith("^")):
            ticker = f"{ticker}.NS"

        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=False)
        if df.empty or len(df) < 30:
            return None

        enriched = enrich_technical_indicators(df)
        return enriched
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def fetch_multiple_stocks(symbols: List[str], period: str = "6mo") -> Dict[str, pd.DataFrame]:
    """
    Fetches and prepares data for a list of stocks.
    """
    results = {}
    for sym in symbols:
        data = fetch_stock_data(sym, period=period)
        if data is not None and not data.empty:
            results[sym] = data
    return results

