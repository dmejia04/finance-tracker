from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from bank.csv_import import load_csv
from transactions.classify import load_transactions
from reports.summary import net_flow, by_group, by_category, concurrent_expenses

console = Console()


@click.group()
def cli():
    """Personal finance tracker."""


@cli.command()
@click.argument("csv_file")
@click.option("--weekly", is_flag=True, help="Show weekly spend breakdown.")
def report(csv_file, weekly):
    """Import a bank CSV and show net flow, categories, and spend."""
    path = Path(csv_file)
    if not path.exists():
        console.print(f"[red]File not found: {csv_file}[/red]")
        raise SystemExit(1)

    raw = load_csv(path)
    console.print(f"[green]Loaded {len(raw)} transactions from {path.name}[/green]\n")

    df = load_transactions(raw)

    # Net flow
    flow = net_flow(df)
    console.print(
        f"[bold]Solde du mois[/bold]  "
        f"Entrées=[green]{flow['income']} €[/green]  "
        f"Sorties=[red]{flow['expenses']} €[/red]  "
        f"Net={'[green]' if flow['net'] >= 0 else '[red]'}{flow['net']} €[/]\n"
    )

    # By group
    groups = by_group(df)
    t = Table(title="Par groupe")
    t.add_column("Groupe")
    t.add_column("Total", justify="right")
    t.add_column("Transactions", justify="right")
    for group, row in groups.iterrows():
        t.add_row(group, f"{row['total']} €", str(int(row["count"])))
    console.print(t)
    console.print()

    # By category
    cats = by_category(df)
    t2 = Table(title="Par catégorie")
    t2.add_column("Groupe")
    t2.add_column("Catégorie")
    t2.add_column("Total", justify="right")
    t2.add_column("Transactions", justify="right")
    for (group, category), row in cats.iterrows():
        t2.add_row(group, category, f"{row['total']} €", str(int(row["count"])))
    console.print(t2)

    # Weekly spend (optional)
    if weekly:
        console.print()
        wk = concurrent_expenses(df)
        t3 = Table(title="Dépenses hebdomadaires")
        t3.add_column("Semaine")
        t3.add_column("Montant", justify="right")
        for _, row in wk.iterrows():
            t3.add_row(str(row["period"].date()), f"{row['spend']} €")
        console.print(t3)


if __name__ == "__main__":
    cli()
