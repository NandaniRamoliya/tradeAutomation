@echo off
title TradeShield Daily Prediction
cd /d "%~dp0"
echo ======================================================================
echo           TRADESHIELD: SCANNING TODAY'S MARKET PREDICTIONS...
echo ======================================================================
echo.
.\.venv\Scripts\python daily_tracker.py
echo.
echo ======================================================================
echo Predictions saved to: DAILY_PREDICTIONS.txt
echo You can open that file anytime or verify these prices on your Groww app!
echo ======================================================================
pause

