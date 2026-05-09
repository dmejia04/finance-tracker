import os
import json
from pathlib import Path
import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from bank.plaid_client import fetch_transactions
from transactions.classify import load_transactions
from reports.summary import net_flow, by_category, concurrent_expenses

load_dotenv()
console = Console()


@click.group()
def cli():
    """Personal finance tracker."""


@cli.command()
@click.option("--days", default=30, help="Number of days to look back.")
@click.option("--save", is_flag=True, help="Save raw transactions to data/.")
def fetch(days, save):
    """Fetch transactions from your bank via Plaid."""
    token = os.environ.get("PLAID_ACCESS_TOKEN")
    if not token:
        console.print("[red]PLAID_ACCESS_TOKEN not set in .env[/red]")
        raise SystemExit(1)

    console.print(f"Fetching last {days} days of transactions...")
    raw = fetch_transactions(token, days=days)
    console.print(f"[green]Fetched {len(raw)} transactions.[/green]")

    if save:
        out = Path("data/transactions.json")
        out.write_text(json.dumps(raw, default=str))
        console.print(f"Saved to {out}")


@cli.command()
@click.option("--file", "src_file", default="data/transactions.json", help="Path to saved transactions JSON.")
def report(src_file):
    """Show net flow, category breakdown, and weekly spend."""
    raw = json.loads(Path(src_file).read_text())
    df = load_transactions(raw)

    flow = net_flow(df)
    console.print(f"\n[bold]Net flow[/bold]  income={flow['income']}  expenses={flow['expenses']}  net={flow['net']}\n")

    cats = by_category(df)
    t = Table(title="Expenses by category")
    t.add_column("Category")
    t.add_column("Total", justify="right")
    t.add_column("Transactions", justify="right")
    for label, row in cats.iterrows():
        t.add_row(label, str(row["total"]), str(int(row["count"])))
    console.print(t)

    weekly = concurrent_expenses(df)
    t2 = Table(title="Weekly spend")
    t2.add_column("Week")
    t2.add_column("Spend", justify="right")
    for _, row in weekly.iterrows():
        t2.add_row(str(row["period"].date()), str(row["spend"]))
    console.print(t2)


if __name__ == "__main__":
    cli()
