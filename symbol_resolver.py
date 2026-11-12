from typing import Tuple, Optional
import requests

COMMON_ALIASES = {
    "GOLD": ("GOLDBEES.NS", "Gold BeES (Nippon India)"),
    "SILVER": ("SILVERBEES.NS", "Silver BeES (Nippon India)"),
    "GOLDBEES": ("GOLDBEES.NS", "Gold BeES (Nippon India)"),
    "SILVERBEES": ("SILVERBEES.NS", "Silver BeES (Nippon India)"),
    "SBI": ("SBIN.NS", "State Bank of India"),
    "TCS": ("TCS.NS", "Tata Consultancy Services"),
    "INFY": ("INFY.NS", "Infosys Limited"),
    "INFOSYS": ("INFY.NS", "Infosys Limited"),
    "RELIANCE": ("RELIANCE.NS", "Reliance Industries Limited"),
    "TATASTEEL": ("TATASTEEL.NS", "Tata Steel Limited"),
    "TATA STEEL": ("TATASTEEL.NS", "Tata Steel Limited"),
    "TATA MOTORS": ("TMCV.NS", "Tata Motors Limited"),
    "TATAMOTORS": ("TMCV.NS", "Tata Motors Limited"),
    "ZOMATO": ("ETERNAL.NS", "Eternal Ltd (Zomato)"),
    "ETERNAL": ("ETERNAL.NS", "Eternal Ltd (Zomato)"),
}


def resolve_stock_symbol(query: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Resolves any user input (company name, colloquial name, typo, or partial name)
    to the official NSE/BSE ticker symbol and company name.

    Returns: (ticker_symbol, company_display_name)
    Example: 'omnitech engineering ltd' -> ('OMNI.NS', 'OMNITECH ENGINEERING LTD')
    """
    clean_q = query.strip().upper()
    if not clean_q:
        return None, None

    # 1. Check direct alias dictionary
    if clean_q in COMMON_ALIASES:
        return COMMON_ALIASES[clean_q]

    # 2. Check if already formatted as standard NSE ticker (e.g. INFY.NS or INFY)
    raw_sym = clean_q.replace(".NS", "").replace(".BO", "")
    if len(raw_sym) <= 12 and " " not in raw_sym:
        # Check if direct ticker works on Yahoo
        candidate = f"{raw_sym}.NS"
        alias_key = raw_sym
        # We also do a quick search query to verify if direct ticker is valid or fuzzy name
    
    # 3. Yahoo Finance Search API for Indian Equities
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            quotes = data.get("quotes", [])
            # Priority: .NS (National Stock Exchange), fallback to .BO (Bombay Stock Exchange)
            ns_quotes = [q for q in quotes if q.get("symbol", "").endswith(".NS")]
            bo_quotes = [q for q in quotes if q.get("symbol", "").endswith(".BO")]
            candidates = ns_quotes + bo_quotes

            if candidates:
                best = candidates[0]
                sym = best["symbol"]
                name = best.get("shortname") or best.get("longname") or sym
                return sym, name
    except Exception:
        pass

    # 4. Fallback: If single word and 1-12 chars, try as NSE ticker directly
    if len(raw_sym) <= 12 and " " not in raw_sym:
        return f"{raw_sym}.NS", raw_sym

    return None, None

