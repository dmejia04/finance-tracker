from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from bank.csv_import import load_csv
from transactions.classify import load_transactions
from reports.summary import net_flow, by_category, concurrent_expenses

console = Console()


@click.group()
def cli():
    """Personal finance tracker."""


@cli.command()
@click.argument("csv_file")
def report(csv_file):
    """Import a bank CSV and show net flow, categories, and weekly spend."""
    path = Path(csv_file)
    if not path.exists():
        console.print(f"[red]File not found: {csv_file}[/red]")
        raise SystemExit(1)

    raw = load_csv(path)
    console.print(f"[green]Loaded {len(raw)} transactions from {path.name}[/green]\n")

    df = load_transactions(raw)

    flow = net_flow(df)
    console.print(
        f"[bold]Net flow[/bold]  "
        f"income=[green]{flow['income']}[/green]  "
        f"expenses=[red]{flow['expenses']}[/red]  "
        f"net={'[green]' if flow['net'] >= 0 else '[red]'}{flow['net']}[/]\n"
    )

    cats = by_category(df)
    t = Table(title="Expenses by category")
    t.add_column("Category")
    t.add_column("Total", justify="right")
    t.add_column("Transactions", justify="right")
    for label, row in cats.iterrows():
        t.add_row(label, f"{row['total']} €", str(int(row["count"])))
    console.print(t)

    weekly = concurrent_expenses(df)
    t2 = Table(title="Weekly spend")
    t2.add_column("Week")
    t2.add_column("Spend", justify="right")
    for _, row in weekly.iterrows():
        t2.add_row(str(row["period"].date()), f"{row['spend']} €")
    console.print(t2)


if __name__ == "__main__":
    cli()
