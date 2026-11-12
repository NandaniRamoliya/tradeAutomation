import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

import config
from shield import TradeShield
from scanner import scan_market, analyze_stock_signal
from data_fetcher import fetch_stock_data, load_stock_universe
from ai_advisor import generate_trade_guidance, get_beginner_shield_tip

console = Console()


def send_telegram_alert(message: str, token: str = "", chat_id: str = "") -> bool:
    """Dispatches alert to Telegram if configured."""
    bot_token = token or config.TELEGRAM_BOT_TOKEN
    target_chat = chat_id or config.TELEGRAM_CHAT_ID
    if not bot_token or not target_chat:
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, json=payload, timeout=8)
        return resp.status_code == 200
    except Exception as e:
        console.print(f"[yellow]Telegram alert failed: {e}[/yellow]")
        return False


def display_signals_table(signals: List[Dict[str, Any]], capital_inr: float):
    """Renders a rich table of all approved triggers."""
    if not signals:
        console.print(Panel(
            "[bold yellow]⚠️ No high-probability setups passed The Shield today.[/bold yellow]\n"
            "This means the market conditions did not meet our strict risk-reward rules.\n"
            "[green]The best trade is sometimes NO trade — your capital remains 100% protected![/green]",
            title="🛡️ TradeShield Guard Active",
            border_style="yellow"
        ))
        return

    table = Table(
        title=f"🚀 TRADESHIELD: APPROVED 1-2 DAY MOMENTUM TRIGGERS (Wallet: ₹{capital_inr:,.0f})",
        header_style="bold cyan",
        border_style="blue"
    )

    table.add_column("Stock", style="bold white", justify="left")
    table.add_column("Action / Score", justify="center")
    table.add_column("Entry Price", justify="right")
    table.add_column("Shield Stop-Loss", style="bold red", justify="right")
    table.add_column("Target 1 (+3-4%)", style="bold green", justify="right")
    table.add_column("Target 2 (+6-8%)", style="bold green", justify="right")
    table.add_column("Groww Qty", justify="center", style="bold yellow")
    table.add_column("Capital Req", justify="right")
    table.add_column("Max Risk", style="red", justify="right")
    table.add_column("R:R", justify="center")

    for s in signals:
        sh = s["shield"]
        score_color = "green" if s["confidence_score"] >= 70 else "yellow"
        action_text = f"[{score_color}]{s['action']}\n({s['confidence_score']}%)[/{score_color}]"

        table.add_row(
            s["symbol"].replace(".NS", ""),
            action_text,
            f"₹{s['entry_price']:.2f}",
            f"₹{sh['stop_loss_price']:.2f}\n(-{sh['sl_percent']}%)",
            f"₹{sh['target_1_price']:.2f}\n(+{sh['target_1_percent']}%)",
            f"₹{sh['target_2_price']:.2f}\n(+{sh['target_2_percent']}%)",
            str(sh["recommended_quantity"]),
            f"₹{sh['total_investment']:,.0f}",
            f"₹{sh['max_possible_loss']:.1f}",
            f"{sh['rr_ratio']}:1"
        )

    console.print(table)


def run_scanner_flow(capital_inr: float, export_file: Optional[str] = None):
    """Executes the full market scanning flow."""
    console.print(Panel(
        f"[bold cyan]🛡️ TradeShield Bot: Scanning Indian Equities (NSE)...[/bold cyan]\n"
        f"• Target Holding: 1 - 2 Days (BTST / Momentum Breakouts)\n"
        f"• Allocated Wallet: ₹{capital_inr:,.2f} | Max Risk/Trade: {config.MAX_RISK_PER_TRADE_PCT*100}%\n"
        f"• {get_beginner_shield_tip()}",
        border_style="cyan"
    ))

    shield = TradeShield(capital_inr=capital_inr)
    signals = scan_market(shield=shield)

    display_signals_table(signals, capital_inr)

    # Print detailed guidance for top 2 signals
    if signals:
        console.print("\n[bold green]📌 STEP-BY-STEP EXECUTION PLANS FOR GROWW:[/bold green]")
        for sig in signals[:2]:
            guidance = generate_trade_guidance(sig, capital_inr)
            console.print(Panel(guidance, border_style="green"))

    # Export if requested
    if export_file:
        export_path = Path(export_file)
        export_data = []
        for s in signals:
            export_data.append({
                "symbol": s["symbol"],
                "action": s["action"],
                "confidence_score": s["confidence_score"],
                "entry_price": s["entry_price"],
                "stop_loss": s["shield"]["stop_loss_price"],
                "target_1": s["shield"]["target_1_price"],
                "target_2": s["shield"]["target_2_price"],
                "quantity": s["shield"]["recommended_quantity"],
                "capital_required": s["shield"]["total_investment"],
                "max_risk_rupees": s["shield"]["max_possible_loss"],
                "reasons": s["reasons"]
            })
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)
        console.print(f"[bold green]✅ Exported {len(signals)} triggers to {export_path}[/bold green]")


def run_single_stock_check(symbol: str, capital_inr: float):
    """Inspects a single stock on demand."""
    shield = TradeShield(capital_inr=capital_inr)
    df = fetch_stock_data(symbol)
    if df is None:
        console.print(f"[bold red]❌ Could not fetch data for '{symbol}'. Check symbol name.[/bold red]")
        return

    sig = analyze_stock_signal(symbol, df, shield)
    if not sig:
        console.print(f"[bold red]❌ Insufficient history for '{symbol}'.[/bold red]")
        return

    sh = sig["shield"]
    if sh["is_approved"]:
        guidance = generate_trade_guidance(sig, capital_inr)
        console.print(Panel(guidance, title=f"🛡️ Analysis for {symbol}", border_style="green"))
    else:
        rejection_txt = "\n • ".join(sh["rejection_reasons"])
        console.print(Panel(
            f"[bold red]🚫 THE SHIELD HAS REJECTED THIS STOCK:[/bold red]\n\n"
            f"• Current Price: ₹{sig['entry_price']:.2f}\n"
            f"• RSI: {sig['rsi']}\n"
            f"• Volume Surge: {sig['volume_surge']}x\n\n"
            f"[bold yellow]Shield Warnings / Why NOT to Buy:[/bold yellow]\n • {rejection_txt}\n\n"
            f"[green]Protection activated: Keeping your capital safe from bad setups![/green]",
            title=f"🛡️ Shield Rejection for {symbol}",
            border_style="red"
        ))

