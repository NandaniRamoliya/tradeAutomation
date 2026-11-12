import math
from typing import Dict, Any, Optional
import config


class TradeShield:
    """
    The 'Shield' protects the trader's capital by:
    1. Vetting trade quality (rejecting low probability / bad R:R trades)
    2. Enforcing strict volatility-based Stop-Loss (prevents deep drawdowns)
    3. Calculating exact position sizing tailored to the user's Groww capital
    """

    def __init__(
        self,
        capital_inr: float = config.DEFAULT_CAPITAL_INR,
        max_risk_pct: float = config.MAX_RISK_PER_TRADE_PCT,
        min_rr_ratio: float = config.MIN_RISK_REWARD_RATIO
    ):
        self.capital_inr = capital_inr
        self.max_risk_pct = max_risk_pct
        self.max_risk_rupees = capital_inr * max_risk_pct
        self.min_rr_ratio = min_rr_ratio

    def evaluate_risk(
        self,
        symbol: str,
        current_price: float,
        atr: float,
        rsi: float,
        ema_50: float,
        ema_200: float,
        volume_surge: float,
        recent_low: float
    ) -> Dict[str, Any]:
        """
        Runs the trade through safety gates.
        Returns risk evaluation and position sizing if approved.
        """
        rejection_reasons = []

        # Gate 1: Trend alignment
        if current_price < ema_50:
            rejection_reasons.append(f"Price (₹{current_price:.2f}) is below 50 EMA (₹{ema_50:.2f}) - Downtrend")
        
        if current_price < ema_200:
            rejection_reasons.append(f"Price is below 200 EMA - Macro weakness")

        # Gate 2: Momentum sweet-spot
        if rsi > 74:
            rejection_reasons.append(f"RSI is {rsi:.1f} (Overbought) - High risk of sudden pullback")
        elif rsi < 48:
            rejection_reasons.append(f"RSI is {rsi:.1f} (Too weak) - Lacks momentum for 1-2 day gain")

        # Gate 3: Volume confirmation
        if volume_surge < 0.85:
            rejection_reasons.append(f"Volume is only {volume_surge:.2f}x average - Lacks institutional interest")

        # --- Dynamic Stop-Loss Calculation ---
        # Stop loss based on 1.5x ATR or just below recent swing low
        atr_sl_distance = max(atr * config.ATR_STOP_LOSS_MULTIPLIER, current_price * 0.012)
        # Cap max stop loss percentage to 2.5% of stock price for short-term trades
        max_allowed_sl_dist = current_price * 0.025
        sl_distance = min(atr_sl_distance, max_allowed_sl_dist)

        stop_loss_price = round(current_price - sl_distance, 2)
        risk_per_share = round(current_price - stop_loss_price, 2)

        if risk_per_share <= 0:
            rejection_reasons.append("Invalid stop-loss calculation")

        # --- Target Calculation ---
        target_1_price = round(current_price + (risk_per_share * 2.0), 2)
        target_2_price = round(current_price + (risk_per_share * 3.5), 2)

        # Risk-to-Reward Ratio Check
        rr_ratio = round((target_1_price - current_price) / (risk_per_share + 1e-9), 2)
        if rr_ratio < self.min_rr_ratio:
            rejection_reasons.append(f"R:R ratio ({rr_ratio}:1) is below shield minimum ({self.min_rr_ratio}:1)")

        # --- Position Sizing & Capital Allocation ---
        # 1. Shares based on risk budget
        shares_by_risk = math.floor(self.max_risk_rupees / (risk_per_share + 1e-9))
        # 2. Shares based on available capital
        shares_by_capital = math.floor(self.capital_inr / current_price)

        recommended_qty = min(shares_by_risk, shares_by_capital)

        if recommended_qty < 1:
            rejection_reasons.append(
                f"Share price (₹{current_price:.2f}) is too high for your capital (₹{self.capital_inr:.2f}) "
                f"under a ₹{self.max_risk_rupees:.2f} max risk limit."
            )

        is_approved = len(rejection_reasons) == 0

        total_investment = round(recommended_qty * current_price, 2)
        max_possible_loss = round(recommended_qty * risk_per_share, 2)
        target_1_profit = round(recommended_qty * (target_1_price - current_price), 2)
        target_2_profit = round(recommended_qty * (target_2_price - current_price), 2)

        target_1_pct = round(((target_1_price - current_price) / current_price) * 100, 2)
        target_2_pct = round(((target_2_price - current_price) / current_price) * 100, 2)
        sl_pct = round(((current_price - stop_loss_price) / current_price) * 100, 2)

        return {
            "symbol": symbol,
            "status": "APPROVED" if is_approved else "REJECTED",
            "is_approved": is_approved,
            "rejection_reasons": rejection_reasons,
            "current_price": current_price,
            "stop_loss_price": stop_loss_price,
            "sl_percent": sl_pct,
            "target_1_price": target_1_price,
            "target_1_percent": target_1_pct,
            "target_2_price": target_2_price,
            "target_2_percent": target_2_pct,
            "risk_per_share": risk_per_share,
            "rr_ratio": rr_ratio,
            "recommended_quantity": recommended_qty,
            "total_investment": total_investment,
            "max_possible_loss": max_possible_loss,
            "max_loss_pct_of_capital": round((max_possible_loss / self.capital_inr) * 100, 2) if self.capital_inr else 0,
            "target_1_profit": target_1_profit,
            "target_2_profit": target_2_profit
        }
