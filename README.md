# 🛡️ TradeShield: AI Helper & Risk-Guarded Trading Bot for Groww (NSE)

TradeShield is a smart algorithmic trading helper and capital protection system built specifically for **Indian Equities (NSE)** and tailored for **Groww** accounts with modest or beginner capital.

It completely eliminates emotional guesswork by:
1. **Scanning the Market** for high-probability 1-2 day momentum and BTST (Buy Today, Sell Tomorrow) setups.
2. **Predicting High-Probability Moves** using trend confluence (EMA 9/21/50/200), RSI momentum, and institutional volume surges.
3. **The "Shield" (Risk Guard)**: Enforces hard stop-losses and calculates the exact number of shares to buy so you **never risk more than 1.5% - 2% of your capital on any trade**.
4. **Guiding Execution**: Generates plain-English step-by-step instructions showing you exact entry, stop-loss, and exit targets in your Groww app.

---

## ⚡ Quick Start

The virtual environment is ready in `.venv`. To run commands:

### 1. Scan the Market for Today's Best 1-2 Day Setups
Run a scan using your allocated Groww capital (default ₹5,000):
```powershell
.\.venv\Scripts\python main.py scan --capital 5000
```
Or export the results to a file:
```powershell
.\.venv\Scripts\python main.py scan --capital 5000 --export signals.json
```

### 2. Check Any Stock On Demand
Want to check if a specific stock is safe to buy on Groww?
```powershell
.\.venv\Scripts\python main.py check TATASTEEL
.\.venv\Scripts\python main.py check INFY
.\.venv\Scripts\python main.py check SBIN
```

### 3. See the Curated Liquid Stock Universe
Shows the list of high-liquidity stocks priced mostly under ₹1000 (ideal for smaller budgets):
```powershell
.\.venv\Scripts\python main.py universe
```

---

## 🛡️ The 4 Shield Rules (How It Protects Your Money)

1. **Cash Delivery Only (Zero Risk of "Capital Becoming 0")**:
   - The bot strictly recommends **Cash Delivery** trades on NSE equities.
   - **Never touch Options or Futures (F&O)** as a beginner — 93% of retail traders lose money in F&O due to time decay and leverage. In cash delivery, you own the shares; they cannot expire or vanish to zero.
2. **Fixed Risk Per Trade (Max 2%)**:
   - Even if you have only ₹5,000, your maximum possible loss on any trade is capped at ~₹95 - ₹100.
3. **Minimum 1:2 Risk-to-Reward**:
   - The bot will NEVER recommend a trade where the potential reward isn't at least double your risk.
   - **Target 1**: +3.5% to +5.0% (Take partial profit on Day 1 or Day 2).
   - **Target 2**: +7.0% to +8.75% (Let runners capture explosive breakout moves).
4. **Strict Stop-Loss Discipline**:
   - If a trade hits the Stop-Loss, exit immediately without hoping or averaging down.

---

## 📱 Telegram Interactive Assistant
Message your personal bot anytime on Telegram:
- Send **any company name or ticker** (e.g. `Tata Motors`, `Omnitech`, `TATASTEEL`, `SBIN`, `Gold`).
- The bot replies with 2 clear guides:
  1. **If You Want to Buy Now:** Safe entry, Groww share quantity, exact stop-loss, and target profit.
  2. **If You Already Own It:** Whether to hold, trailing stop-loss level, and take-profit target.

To start the interactive bot listener:
```powershell
.\.venv\Scripts\python telegram_listener.py
# Or double-click: RunTelegramBotService.bat
```

---

## 🔍 Logic Verification & Backtesting
Verify how previous predictions performed against real market data:
```powershell
.\.venv\Scripts\python main.py verify
# Or double-click: VerifyResults.bat
```
Run backtest simulation on 30+ low-value / budget-friendly NSE stocks:
```powershell
.\.venv\Scripts\python run_low_value_universe_test.py
```

---

## 📁 Project Structure

- [`config.py`](file:///d:/tradeAutomation/config.py): User capital, risk tolerance, and stop-loss/target parameters.
- [`shield.py`](file:///d:/tradeAutomation/shield.py): The risk engine — validates R:R, computes volatility ATR stop-loss, and exact position size.
- [`indicators.py`](file:///d:/tradeAutomation/indicators.py): Technical formulas (EMA 9/21/50/200, RSI, ATR, Volume Surge, 5-Day Breakout).
- [`symbol_resolver.py`](file:///d:/tradeAutomation/symbol_resolver.py): Smart fuzzy search resolving company names to official NSE tickers.
- [`telegram_listener.py`](file:///d:/tradeAutomation/telegram_listener.py): 24/7 interactive Telegram bot listening and answering user stock queries.
- [`daily_tracker.py`](file:///d:/tradeAutomation/daily_tracker.py): Automated daily prediction scanner (Gold/Silver dip + top momentum stocks).
- [`verifier.py`](file:///d:/tradeAutomation/verifier.py): Logic verification engine comparing past predictions with real market outcomes.
- [`data_fetcher.py`](file:///d:/tradeAutomation/data_fetcher.py): Real-time historical market candle fetcher for NSE stocks.
- [`scanner.py`](file:///d:/tradeAutomation/scanner.py): Market scanner & confidence scoring engine (0-100%).
- [`ai_advisor.py`](file:///d:/tradeAutomation/ai_advisor.py): Generates step-by-step execution cards for Groww.
- [`bot.py`](file:///d:/tradeAutomation/bot.py): Formats output with Rich tables and handles Telegram alerts.
- [`main.py`](file:///d:/tradeAutomation/main.py): CLI interface (`scan`, `check`, `test`, `verify`, `universe`).
- [`RunDailyPrediction.bat`](file:///d:/tradeAutomation/RunDailyPrediction.bat): 1-click daily market prediction generator.
- [`RunTelegramBotService.bat`](file:///d:/tradeAutomation/RunTelegramBotService.bat): 1-click launcher for the interactive Telegram bot.
- [`VerifyResults.bat`](file:///d:/tradeAutomation/VerifyResults.bat): 1-click logic verification against real market data.
