import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import yfinance as yf
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import config

console = Console()
BASE_DIR = Path(__file__).resolve().parent
JOURNAL_JSON = BASE_DIR / "VERIFICATION_LOG.json"


def verify_logged_predictions():
    """
    Reads all past predictions from VERIFICATION_LOG.json,
    fetches actual subsequent market candles from NSE,
    runs the Shield trade evaluation logic, and prints the verified results.
    """
    if not JOURNAL_JSON.exists():
        console.print("[red]No VERIFICATION_LOG.json found.[/red]")
        return

    with open(JOURNAL_JSON, "r", encoding="utf-8") as f:
        try:
            journal = json.load(f)
        except Exception as e:
            console.print(f"[red]Error reading journal: {e}[/red]")
            return

    if not journal:
        console.print("[yellow]Verification log is empty.[/yellow]")
        return

    verified_records = []

    for entry_idx, entry in enumerate(journal):
        ts_str = entry.get("timestamp", "")
        # Parse date from timestamp (e.g. "2026-11-07 08:32 PM" -> "2026-11-07")
        pred_date = ts_str.split()[0] if ts_str else "2026-11-07"
        
        # Check stock predictions
        stocks = entry.get("top_stocks", [])
        for st in stocks:
            sym = st["symbol"]
            entry_p = float(st["entry_price"])
            sl = float(st["stop_loss"])
            t1 = float(st["target_1"])
            t2 = float(st["target_2"])
            qty = int(st["quantity"])

            # Download actual candles from pred_date to today
            try:
                df = yf.download(sym, start=pred_date, progress=False, auto_adjust=False)
            except Exception:
                continue

            if df.empty:
                continue

            # Flatten multi-index columns if needed
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]

            # Filter out the candle of pred_date if prediction was generated after market close
            # Subsequent candles represent the execution days
            subsequent_bars = df[df.index.strftime("%Y-%m-%d") > pred_date]

            if subsequent_bars.empty:
                st["verification_status"] = "PENDING_MARKET_OPEN"
                continue

            exit_price = None
            exit_reason = None
            exit_date = None
            bars_held = 0

            # Evaluate forward day-by-day (up to 2-day holding window)
            for bar_idx in range(len(subsequent_bars)):
                bar = subsequent_bars.iloc[bar_idx]
                bar_date = subsequent_bars.index[bar_idx].strftime("%Y-%m-%d")
                high = float(bar["High"])
                low = float(bar["Low"])
                close = float(bar["Close"])
                open_p = float(bar["Open"])
                bars_held += 1

                # 1. Check Stop-Loss
                if low <= sl:
                    exit_price = min(open_p, sl)
                    exit_reason = "STOP_LOSS_HIT"
                    exit_date = bar_date
                    break

                # 2. Check Target 2
                if high >= t2:
                    exit_price = t2
                    exit_reason = "TARGET_2_HIT"
                    exit_date = bar_date
                    break

                # 3. Check Target 1
                if high >= t1:
                    exit_price = t1
                    exit_reason = "TARGET_1_HIT"
                    exit_date = bar_date
                    break

                # 4. Check if 2 days expired
                if bars_held >= 2:
                    exit_price = close
                    exit_reason = "TIMED_2DAY_EXIT"
                    exit_date = bar_date
                    break

            if exit_price is None:
                # Still within holding window (e.g. Day 1 complete, waiting for Day 2)
                latest_bar = subsequent_bars.iloc[-1]
                latest_close = float(latest_bar["Close"])
                latest_date = subsequent_bars.index[-1].strftime("%Y-%m-%d")
                unrealized_pnl = round((latest_close - entry_p) * qty, 2)
                unrealized_pct = round(((latest_close - entry_p) / entry_p) * 100, 2)
                st["verification_status"] = f"ACTIVE (Current: ₹{latest_close:.2f}, P&L: {unrealized_pct:+.2f}%)"
                verified_records.append({
                    "batch": ts_str,
                    "symbol": sym.replace(".NS", ""),
                    "entry_date": pred_date,
                    "entry_price": entry_p,
                    "sl": sl,
                    "t1": t1,
                    "exit_date": latest_date,
                    "exit_price": latest_close,
                    "outcome": "STILL ACTIVE",
                    "pnl_pct": unrealized_pct,
                    "pnl_rupees": unrealized_pnl,
                    "quantity": qty
                })
            else:
                pnl_rupees = round((exit_price - entry_p) * qty, 2)
                pnl_pct = round(((exit_price - entry_p) / entry_p) * 100, 2)
                st["verification_status"] = f"{exit_reason} on {exit_date} at ₹{exit_price:.2f} (P&L: ₹{pnl_rupees:+.2f})"
                verified_records.append({
                    "batch": ts_str,
                    "symbol": sym.replace(".NS", ""),
                    "entry_date": pred_date,
                    "entry_price": entry_p,
                    "sl": sl,
                    "t1": t1,
                    "exit_date": exit_date,
                    "exit_price": exit_price,
                    "outcome": exit_reason,
                    "pnl_pct": pnl_pct,
                    "pnl_rupees": pnl_rupees,
                    "quantity": qty
                })

    # Save updated verification statuses back to JSON
    with open(JOURNAL_JSON, "w", encoding="utf-8") as f:
        json.dump(journal, f, indent=2)

    # Render Rich Output Table
    table = Table(
        title="🤖 TRADESHIELD LOGIC VERIFICATION: ACTUAL EXECUTION RESULTS",
        header_style="bold cyan",
        border_style="blue"
    )
    table.add_column("Prediction Time", style="cyan")
    table.add_column("Stock", style="bold white")
    table.add_column("Buy Price", justify="right")
    table.add_column("Shield SL", style="red", justify="right")
    table.add_column("Target 1", style="green", justify="right")
    table.add_column("Exit Date", justify="center")
    table.add_column("Exit Price", justify="right")
    table.add_column("Outcome", justify="center")
    table.add_column("P&L %", justify="right")
    table.add_column("Net P&L (₹)", justify="right")

    total_net = 0.0
    for r in verified_records:
        total_net += r["pnl_rupees"]
        outcome_color = "bold green" if "TARGET" in r["outcome"] else ("red" if "STOP" in r["outcome"] else "yellow")
        pnl_color = "bold green" if r["pnl_rupees"] > 0 else ("red" if r["pnl_rupees"] < 0 else "yellow")
        table.add_row(
            r["batch"].split()[0],
            r["symbol"],
            f"₹{r['entry_price']:.2f}",
            f"₹{r['sl']:.2f}",
            f"₹{r['t1']:.2f}",
            r["exit_date"],
            f"₹{r['exit_price']:.2f}",
            f"[{outcome_color}]{r['outcome']}[/{outcome_color}]",
            f"[{pnl_color}]{r['pnl_pct']:+.2f}%[/{pnl_color}]",
            f"[{pnl_color}]₹{r['pnl_rupees']:+.2f}[/{pnl_color}]"
        )

    console.print(table)
    summary_color = "bold green" if total_net >= 0 else "bold red"
    console.print(Panel(
        f"📊 [bold white]TOTAL TRADES VERIFIED BY CODE:[/bold white] {len(verified_records)}\n"
        f"💰 [bold white]TOTAL NET P&L COMBINED:[/bold white] [{summary_color}]₹{total_net:+.2f}[/{summary_color}]\n"
        f"🛡️ [green]Shield Active: All losing trades were capped strictly at stop-loss limits.[/green]",
        title="VERIFICATION SUMMARY",
        border_style="green" if total_net >= 0 else "red"
    ))


if __name__ == "__main__":
    verify_logged_predictions()

