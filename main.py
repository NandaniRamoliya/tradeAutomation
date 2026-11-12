import argparse
import sys
import config
from bot import run_scanner_flow, run_single_stock_check, console
from ai_advisor import get_beginner_shield_tip
from data_fetcher import load_stock_universe
from backtester import TradeShieldBacktester, display_backtest_results
from verifier import verify_logged_predictions


def main():
    parser = argparse.ArgumentParser(
        description="TradeShield: AI Helper & Risk-Guarded Trading Bot for Indian Equities (Groww)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: scan
    scan_parser = subparsers.add_parser("scan", help="Scan NSE market for approved 1-2 day momentum trades")
    scan_parser.add_argument(
        "--capital",
        type=float,
        default=config.DEFAULT_CAPITAL_INR,
        help=f"Your allocated trading capital in Groww (INR). Default: ₹{config.DEFAULT_CAPITAL_INR}"
    )
    scan_parser.add_argument(
        "--export",
        type=str,
        default=None,
        help="Path to export triggers as a JSON file (e.g. triggers.json)"
    )

    # Command: check
    check_parser = subparsers.add_parser("check", help="Check and analyze a single stock symbol on demand")
    check_parser.add_argument("symbol", type=str, help="Stock symbol (e.g. TATASTEEL, INFY, BEL, ZOMATO)")
    check_parser.add_argument(
        "--capital",
        type=float,
        default=config.DEFAULT_CAPITAL_INR,
        help=f"Your allocated trading capital in Groww (INR). Default: ₹{config.DEFAULT_CAPITAL_INR}"
    )

    # Command: universe
    subparsers.add_parser("universe", help="View the list of curated liquid stocks under ₹1000")

    # Command: tip
    subparsers.add_parser("tip", help="Get a quick risk management tip from the Shield")

    # Command: test (Backtesting / Historical Verification)
    test_parser = subparsers.add_parser("test", help="Backtest the logic on past data (zero lookahead bias)")
    test_parser.add_argument("--period", type=str, default="3mo", help="Backtest period (e.g. 1mo, 3mo, 6mo). Default: 3mo")
    test_parser.add_argument("--capital", type=float, default=config.DEFAULT_CAPITAL_INR, help="Simulated wallet capital. Default: ₹5000")
    test_parser.add_argument("--symbol", type=str, default=None, help="Optional: Test a specific single stock (e.g. TATASTEEL)")

    # Command: verify (Live Performance Verification)
    subparsers.add_parser("verify", help="Verify logged daily predictions against actual market data")

    args = parser.parse_args()

    if args.command == "verify":
        verify_logged_predictions()
    elif args.command == "test":
        backtester = TradeShieldBacktester(capital_inr=args.capital)
        symbols = [args.symbol] if args.symbol else None
        stats = backtester.run_backtest_universe(symbols=symbols, period=args.period)
        display_backtest_results(stats)
    elif args.command == "scan":
        run_scanner_flow(capital_inr=args.capital, export_file=args.export)
    elif args.command == "check":
        run_single_stock_check(symbol=args.symbol, capital_inr=args.capital)
    elif args.command == "universe":
        symbols = load_stock_universe()
        console.print(f"[bold cyan]Curated Liquid Universe ({len(symbols)} stocks):[/bold cyan]")
        for i, s in enumerate(symbols, 1):
            console.print(f" {i}. {s.replace('.NS', '')}")
    elif args.command == "tip":
        console.print(f"\n{get_beginner_shield_tip()}\n")
    else:
        # Default behavior if no command provided: run scan with default capital
        run_scanner_flow(capital_inr=config.DEFAULT_CAPITAL_INR)


if __name__ == "__main__":
    main()

