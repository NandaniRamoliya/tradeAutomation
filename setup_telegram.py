import sys
import requests
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def test_telegram_creds(token: str, chat_id: str) -> bool:
    """Sends a verification ping to Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": (
            "🛡️ *TRADESHIELD ALERT SYSTEM CONNECTED!*\n\n"
            "✅ Your Telegram bot is now linked to TradeShield.\n"
            "Every weekday at *9:00 AM* and *4:00 PM*, today's best low-value stock picks and Gold/Silver dip alerts will be delivered right here to your phone!\n\n"
            "Happy stress-free trading! 🚀"
        ),
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if resp.status_code == 200 and data.get("ok"):
            return True
        else:
            console.print(f"[bold red]❌ Telegram API Error: {data.get('description', 'Unknown error')}[/bold red]")
            return False
    except Exception as e:
        console.print(f"[bold red]❌ Network error contacting Telegram: {e}[/bold red]")
        return False


def save_env(token: str, chat_id: str):
    """Writes credentials to .env file."""
    lines = []
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not (line.startswith("TELEGRAM_BOT_TOKEN") or line.startswith("TELEGRAM_CHAT_ID")):
                    lines.append(line.rstrip())

    lines.append(f"TELEGRAM_BOT_TOKEN={token}")
    lines.append(f"TELEGRAM_CHAT_ID={chat_id}")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def setup_telegram_interactive(token: str = None, chat_id: str = None):
    console.print(Panel(
        "[bold cyan]📱 TRADESHIELD: TELEGRAM BOT SETUP[/bold cyan]\n\n"
        "To receive your daily recommendations directly on your smartphone:\n"
        "1. Open Telegram and search for [bold yellow]@BotFather[/bold yellow]\n"
        "   • Send: [green]/newbot[/green]\n"
        "   • Give it a name (e.g., MyTradeShieldBot)\n"
        "   • BotFather gives you an [bold green]API Token[/bold green] (like: 123456789:ABCdef...)\n\n"
        "2. Open your new bot and click [bold green]START[/bold green] (or send 'hi')\n\n"
        "3. Search for [bold yellow]@userinfobot[/bold yellow] on Telegram\n"
        "   • It will immediately reply with your personal [bold green]Id[/bold green] (e.g. 987654321)",
        border_style="cyan"
    ))

    bot_token = token or input("\n👉 Paste your Telegram Bot Token: ").strip()
    user_id = chat_id or input("👉 Paste your Telegram Chat ID: ").strip()

    if not bot_token or not user_id:
        console.print("[red]Token or Chat ID cannot be empty.[/red]")
        return False

    console.print("\n[yellow]⏳ Testing connection by sending a message to your Telegram...[/yellow]")
    if test_telegram_creds(bot_token, user_id):
        save_env(bot_token, user_id)
        console.print(Panel(
            "[bold green]🎉 SUCCESS! Check your Telegram phone app now.[/bold green]\n"
            "You should see the confirmation message from your TradeShield bot.\n"
            "Your credentials have been securely saved to .env.\n"
            "All daily automated scans will now send straight to your phone!",
            border_style="green"
        ))
        return True
    else:
        console.print("[bold red]Connection failed. Please double check your Bot Token and Chat ID.[/bold red]")
        return False


if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else None
    c = sys.argv[2] if len(sys.argv) > 2 else None
    setup_telegram_interactive(t, c)

