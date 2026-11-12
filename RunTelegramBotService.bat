@echo off
title TradeShield Telegram Interactive Bot
cd /d "%~dp0"
echo ======================================================================
echo           TRADESHIELD: TELEGRAM INTERACTIVE BOT IS RUNNING...
echo ======================================================================
echo.
echo Anyone can now open Telegram and message: @nandan_trade_bot
echo Type any stock name (e.g. TATASTEEL, SBIN, IRFC, INFY) to get instant advice!
echo.
echo Keep this window open in the background to keep the bot active.
echo ======================================================================
echo.
.\.venv\Scripts\python telegram_listener.py
pause

