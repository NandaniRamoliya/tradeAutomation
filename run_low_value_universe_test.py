import json
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import config
from data_fetcher import load_stock_universe, fetch_stock_data
from backtester import TradeShieldBacktester, display_backtest_results

console = Console()


def run_minimum_value_stocks_test(period: str = "3mo", capital_inr: float = 5000.0):
    """
    Runs the TradeShield algorithm across all low-value / affordable stocks
    over recent real market data and outputs verified buy/sell execution results.
    """
    symbols = load_stock_universe()
    # Filter out commodity ETFs for stock momentum test
    stock_symbols = [s for s in symbols if "BEES" not in s]

    console.print(Panel(
        f"[bold cyan]🔍 TESTING TRADESHIELD ON LOW-VALUE / MINIMUM BUDGET STOCKS[/bold cyan]\n"
        f"• Total Stocks in Universe: {len(stock_symbols)} (All low share prices ₹50 - ₹450)\n"
        f"• Historical Test Window: Last {period} of real market trading\n"
        f"• Simulated Wallet: ₹{capital_inr:,.0f} | Max Risk Per Trade: 2% (~₹100)\n"
        f"• Strict Rule: Algorithm only sees past candles; zero lookahead bias",
        border_style="cyan"
    ))

    backtester = TradeShieldBacktester(
        capital_inr=capital_inr,
        max_holding_days=2,
        min_confidence=65
    )

    stats = backtester.run_backtest_universe(symbols=stock_symbols, period=period)
    display_backtest_results(stats)

    trades = stats.get("trades", [])
    if trades:
        # Show breakdown of low-value stock executions
        price_ranges = {
            "Under ₹100 (Ultra Budget)": [t for t in trades if t.entry_price < 100],
            "₹100 to ₹250 (Mid Budget)": [t for t in trades if 100 <= t.entry_price <= 250],
            "₹250 to ₹450 (Higher Budget)": [t for t in trades if t.entry_price > 250],
        }

        cat_table = Table(
            title="📊 PERFORMANCE BREAKDOWN BY SHARE PRICE CATEGORY",
            header_style="bold magenta",
            border_style="cyan"
        )
        cat_table.add_column("Price Category", style="bold white")
        cat_table.add_column("Trades", justify="center")
        cat_table.add_column("Wins", justify="center", style="green")
        cat_table.add_column("Losses", justify="center", style="red")
        cat_table.add_column("Win Rate %", justify="right")
        cat_table.add_column("Total P&L (₹)", justify="right")

        for cat_name, cat_trades in price_ranges.items():
            if not cat_trades:
                continue
            cat_wins = [t for t in cat_trades if t.pnl_rupees > 0]
            cat_losses = [t for t in cat_trades if t.pnl_rupees < 0]
            cat_wr = (len(cat_wins) / len(cat_trades)) * 100 if cat_trades else 0
            cat_pnl = sum(t.pnl_rupees for t in cat_trades)
            pnl_style = "bold green" if cat_pnl >= 0 else "bold red"

            cat_table.add_row(
                cat_name,
                str(len(cat_trades)),
                str(len(cat_wins)),
                str(len(cat_losses)),
                f"{cat_wr:.1f}%",
                f"[{pnl_style}]₹{cat_pnl:+,.2f}[/{pnl_style}]"
            )

        console.print(cat_table)


if __name__ == "__main__":
    run_minimum_value_stocks_test(period="3mo", capital_inr=5000.0)

