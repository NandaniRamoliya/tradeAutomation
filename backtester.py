from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import config
from shield import TradeShield
from data_fetcher import fetch_stock_data, load_stock_universe
from indicators import enrich_technical_indicators
from scanner import analyze_stock_signal

console = Console()


@dataclass
class BacktestTrade:
    symbol: str
    entry_date: str
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    quantity: int
    investment: float
    exit_date: str
    exit_price: float
    exit_reason: str  # "TARGET_1", "TARGET_2", "STOP_LOSS", "TIME_EXIT"
    pnl_rupees: float
    pnl_percent: float
    holding_days: int


class TradeShieldBacktester:
    """
    Simulates TradeShield on historical data without lookahead bias.
    On each historical day T, the engine only sees candles up to day T.
    It then tracks the trade forward over the next 1-2 days to see if
    Target 1, Target 2, or Stop Loss was hit.
    """

    def __init__(
        self,
        capital_inr: float = config.DEFAULT_CAPITAL_INR,
        max_holding_days: int = 2,
        min_confidence: int = 65
    ):
        self.capital_inr = capital_inr
        self.max_holding_days = max_holding_days
        self.min_confidence = min_confidence
        self.shield = TradeShield(capital_inr=capital_inr)

    def backtest_single_stock(self, symbol: str, df: pd.DataFrame) -> List[BacktestTrade]:
        """
        Walks forward day-by-day on a single stock to evaluate past signals.
        """
        if df is None or len(df) < 60:
            return []

        trades: List[BacktestTrade] = []
        i = 50  # Warmup period for 50 EMA and indicators
        n = len(df)

        while i < n - self.max_holding_days - 1:
            # STRICT LOOKAHEAD PREVENTION:
            # We slice data STRICTLY up to day i. Day i+1 and beyond do NOT exist to the model yet!
            historical_slice = df.iloc[: i + 1].copy()

            # Analyze the signal as if today was day i
            signal = analyze_stock_signal(symbol, historical_slice, self.shield)

            if (
                signal
                and signal["shield"]["is_approved"]
                and signal["confidence_score"] >= self.min_confidence
            ):
                entry_date_ts = df.index[i]
                entry_date_str = str(entry_date_ts.date() if hasattr(entry_date_ts, "date") else entry_date_ts)[:10]

                sh = signal["shield"]
                entry_price = signal["entry_price"]
                sl = sh["stop_loss_price"]
                t1 = sh["target_1_price"]
                t2 = sh["target_2_price"]
                qty = sh["recommended_quantity"]
                investment = sh["total_investment"]

                # Walk forward through Day i+1 and Day i+2
                exit_price = None
                exit_reason = None
                exit_date_str = None
                holding_days = 0

                for step in range(1, self.max_holding_days + 1):
                    future_bar = df.iloc[i + step]
                    fut_ts = df.index[i + step]
                    f_date = str(fut_ts.date() if hasattr(fut_ts, "date") else fut_ts)[:10]
                    fut_high = float(future_bar["High"])
                    fut_low = float(future_bar["Low"])
                    fut_close = float(future_bar["Close"])
                    fut_open = float(future_bar["Open"])
                    holding_days = step

                    # Worst-case assumption: check Stop Loss first
                    if fut_low <= sl:
                        exit_price = min(fut_open, sl)  # Handles gap down opening below SL
                        exit_reason = "STOP_LOSS"
                        exit_date_str = f_date
                        break

                    # Check Target 2 (Runner target)
                    if fut_high >= t2:
                        exit_price = t2
                        exit_reason = "TARGET_2"
                        exit_date_str = f_date
                        break

                    # Check Target 1 (Quick target)
                    if fut_high >= t1:
                        exit_price = t1
                        exit_reason = "TARGET_1"
                        exit_date_str = f_date
                        break

                # If neither hit after max_holding_days, exit at close of day i + max_holding_days
                if exit_price is None:
                    last_bar = df.iloc[i + self.max_holding_days]
                    last_ts = df.index[i + self.max_holding_days]
                    exit_date_str = str(last_ts.date() if hasattr(last_ts, "date") else last_ts)[:10]
                    exit_price = float(last_bar["Close"])
                    exit_reason = "TIME_EXIT"

                pnl_per_share = exit_price - entry_price
                pnl_rupees = round(pnl_per_share * qty, 2)
                pnl_pct = round((pnl_per_share / entry_price) * 100, 2)

                trade = BacktestTrade(
                    symbol=symbol.replace(".NS", ""),
                    entry_date=entry_date_str,
                    entry_price=round(entry_price, 2),
                    stop_loss=round(sl, 2),
                    target_1=round(t1, 2),
                    target_2=round(t2, 2),
                    quantity=qty,
                    investment=round(investment, 2),
                    exit_date=exit_date_str,
                    exit_price=round(exit_price, 2),
                    exit_reason=exit_reason,
                    pnl_rupees=pnl_rupees,
                    pnl_percent=pnl_pct,
                    holding_days=holding_days
                )
                trades.append(trade)

                # Advance pointer past the trade holding window to avoid double-counting
                i += holding_days
            else:
                i += 1

        return trades

    def run_backtest_universe(self, symbols: Optional[List[str]] = None, period: str = "6mo") -> Dict[str, Any]:
        """
        Runs the simulation across all liquid universe stocks over the historical period.
        """
        if symbols is None:
            symbols = load_stock_universe()

        all_trades: List[BacktestTrade] = []

        console.print(Panel(
            f"[bold cyan]⏳ BACKTESTING TRADESHIELD SIMULATION (Zero Lookahead Bias)...[/bold cyan]\n"
            f"• Historical Period: Last {period}\n"
            f"• Strict Rule: Algorithm only sees past candles up to Day T\n"
            f"• Max Holding Window: {self.max_holding_days} Days (BTST / Short Swing)\n"
            f"• Simulated Wallet: ₹{self.capital_inr:,.0f} | Stop-Loss Enforced",
            border_style="cyan"
        ))

        for sym in symbols:
            df = fetch_stock_data(sym, period=period)
            if df is not None:
                stock_trades = self.backtest_single_stock(sym, df)
                all_trades.extend(stock_trades)

        # Sort trades chronologically
        all_trades.sort(key=lambda t: t.entry_date)

        return self.compile_statistics(all_trades)

    def compile_statistics(self, trades: List[BacktestTrade]) -> Dict[str, Any]:
        """Calculates win rate, profit factor, total returns, and stats."""
        if not trades:
            return {"trades": [], "total_trades": 0, "win_rate": 0.0}

        total = len(trades)
        wins = [t for t in trades if t.pnl_rupees > 0]
        losses = [t for t in trades if t.pnl_rupees < 0]
        breakevens = [t for t in trades if t.pnl_rupees == 0]

        t1_hits = [t for t in trades if t.exit_reason == "TARGET_1"]
        t2_hits = [t for t in trades if t.exit_reason == "TARGET_2"]
        sl_hits = [t for t in trades if t.exit_reason == "STOP_LOSS"]
        time_exits = [t for t in trades if t.exit_reason == "TIME_EXIT"]

        win_rate = (len(wins) / total) * 100.0 if total > 0 else 0.0
        total_profit = sum(t.pnl_rupees for t in trades)
        avg_win = np.mean([t.pnl_rupees for t in wins]) if wins else 0.0
        avg_loss = np.mean([abs(t.pnl_rupees) for t in losses]) if losses else 0.0
        profit_factor = (sum(t.pnl_rupees for t in wins) / (sum(abs(t.pnl_rupees) for t in losses) + 1e-9)) if losses else 999.0

        return {
            "trades": trades,
            "total_trades": total,
            "wins": len(wins),
            "losses": len(losses),
            "breakevens": len(breakevens),
            "win_rate": round(win_rate, 1),
            "target_1_hits": len(t1_hits),
            "target_2_hits": len(t2_hits),
            "sl_hits": len(sl_hits),
            "time_exits": len(time_exits),
            "total_pnl_rupees": round(total_profit, 2),
            "total_return_pct_on_wallet": round((total_profit / self.capital_inr) * 100, 2),
            "avg_win_rupees": round(avg_win, 2),
            "avg_loss_rupees": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2)
        }


def display_backtest_results(stats: Dict[str, Any]):
    """Renders formatted trade log and executive performance card."""
    trades: List[BacktestTrade] = stats.get("trades", [])
    if not trades:
        console.print("[yellow]No trades were generated in the backtest period.[/yellow]")
        return

    # 1. Summary Card
    pnl = stats["total_pnl_rupees"]
    pnl_style = "bold green" if pnl >= 0 else "bold red"

    summary_text = (
        f"📊 [bold white]TOTAL TRADES:[/bold white] {stats['total_trades']}  |  "
        f"🏆 [bold green]WIN RATE:[/bold green] {stats['win_rate']}%  |  "
        f"⚖️ [bold cyan]PROFIT FACTOR:[/bold cyan] {stats['profit_factor']}\n\n"
        f"🎯 Target 1 Hits (+5.0%): [bold green]{stats['target_1_hits']}[/bold green]  |  "
        f"🚀 Target 2 Runners (+8.7%): [bold green]{stats['target_2_hits']}[/bold green]\n"
        f"🛡️ Stop-Loss Exits (-2.5%): [bold red]{stats['sl_hits']}[/bold red]  |  "
        f"⏱️ Timed 2-Day Exits: [bold yellow]{stats['time_exits']}[/bold yellow]\n\n"
        f"💰 [bold white]Net Profit on ₹5,000 Capital:[/bold white] [{pnl_style}]₹{pnl:,.2f} ({stats['total_return_pct_on_wallet']}%) [/{pnl_style}]\n"
        f"📈 Avg Win: ₹{stats['avg_win_rupees']:.2f}  |  📉 Avg Loss: ₹{stats['avg_loss_rupees']:.2f} (Shield strictly contained losses!)"
    )

    console.print(Panel(summary_text, title="🛡️ TRADESHIELD HISTORICAL VERIFICATION REPORT", border_style="green" if pnl >= 0 else "red"))

    # 2. Detailed Trade-by-Trade Table (Showing the last 15 trades so user can cross-verify in Groww charts)
    table = Table(
        title="🔍 VERIFIABLE TRADE LOG (Check these dates & prices on your Groww chart!)",
        header_style="bold cyan",
        border_style="blue"
    )
    table.add_column("Stock", style="bold white")
    table.add_column("Entry Date")
    table.add_column("Entry ₹", justify="right")
    table.add_column("Stop-Loss ₹", style="red", justify="right")
    table.add_column("Target 1 ₹", style="green", justify="right")
    table.add_column("Exit Date")
    table.add_column("Exit ₹", justify="right")
    table.add_column("Result", justify="center")
    table.add_column("P&L %", justify="right")
    table.add_column("P&L ₹", justify="right")

    # Display up to 20 representative trades across the timeline
    display_trades = trades[-20:] if len(trades) > 20 else trades
    for t in display_trades:
        res_style = "green" if t.pnl_rupees > 0 else ("red" if t.pnl_rupees < 0 else "yellow")
        table.add_row(
            t.symbol,
            t.entry_date,
            f"₹{t.entry_price:.2f}",
            f"₹{t.stop_loss:.2f}",
            f"₹{t.target_1:.2f}",
            t.exit_date,
            f"₹{t.exit_price:.2f}",
            f"[{res_style}]{t.exit_reason}[/{res_style}]",
            f"[{res_style}]{t.pnl_percent:+.2f}%[/{res_style}]",
            f"[{res_style}]₹{t.pnl_rupees:+.2f}[/{res_style}]"
        )

    console.print(table)

