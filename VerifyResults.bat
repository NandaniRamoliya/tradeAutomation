@echo off
title TradeShield Logic Verification
cd /d "%~dp0"
echo ======================================================================
echo           TRADESHIELD: VERIFYING PREDICTIONS AGAINST REAL MARKET
echo ======================================================================
echo.
.\.venv\Scripts\python verifier.py
echo.
echo ======================================================================
pause

