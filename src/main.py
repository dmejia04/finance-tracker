from pathlib import Path
import click
import pandas as pd
from rich.console import Console
from rich.table import Table

from bank.csv_import import load_csv
from transactions.classify import load_transactions
from reports.summary import net_flow, by_group, by_category, concurrent_expenses
from reports.charts import monthly_net_flow, category_pie, weekly_spend_bar
from reports.budget import load_budget, check_alerts

console = Console()
BUDGET_FILE = Path(__file__).parent.parent / "budget.toml"


def _load(*csv_files) -> pd.DataFrame:
    frames = []
    for f in csv_files:
        raw = load_csv(f)
        frames.append(load_transactions(raw))
    df = pd.concat(frames, ignore_index=True)
    console.print(f"[green]Loaded {len(df)} transactions from {len(csv_files)} file(s)[/green]\n")
    return df


def _filter_month(df: pd.DataFrame, month: str | None) -> pd.DataFrame:
    if not month:
        return df
    mask = df["date"].dt.to_period("M").astype(str) == month
    filtered = df[mask]
    if filtered.empty:
        console.print(f"[yellow]No transactions found for {month}[/yellow]")
        raise SystemExit(0)
    return filtered


@click.group()
def cli():
    """Personal finance tracker."""


@cli.command()
@click.argument("csv_files", nargs=-1, required=True)
@click.option("--month", default=None, help="Filter by month, e.g. 2026-01")
@click.option("--weekly", is_flag=True, help="Show weekly spend table.")
@click.option("--alerts", is_flag=True, help="Show budget alerts.")
def report(csv_files, month, weekly, alerts):
    """Show net flow and category breakdown. Accepts one or more CSV files."""
    df = _load(*csv_files)
    view = _filter_month(df, month)
    label = f" — {month}" if month else ""

    # Net flow
    flow = net_flow(view)
    console.print(
        f"[bold]Solde{label}[/bold]  "
        f"Entrées=[green]{flow['income']} €[/green]  "
        f"Sorties=[red]{flow['expenses']} €[/red]  "
        f"Net={'[green]' if flow['net'] >= 0 else '[red]'}{flow['net']} €[/]\n"
    )

    # By group
    groups = by_group(view)
    t = Table(title=f"Par groupe{label}")
    t.add_column("Groupe")
    t.add_column("Total", justify="right")
    t.add_column("Transactions", justify="right")
    for group, row in groups.iterrows():
        t.add_row(group, f"{row['total']} €", str(int(row["count"])))
    console.print(t)
    console.print()

    # By category
    cats = by_category(view)
    t2 = Table(title=f"Par catégorie{label}")
    t2.add_column("Groupe")
    t2.add_column("Catégorie")
    t2.add_column("Total", justify="right")
    t2.add_column("Transactions", justify="right")
    for (group, category), row in cats.iterrows():
        t2.add_row(group, category, f"{row['total']} €", str(int(row["count"])))
    console.print(t2)

    # Weekly spend
    if weekly:
        console.print()
        wk = concurrent_expenses(view)
        t3 = Table(title="Dépenses hebdomadaires")
        t3.add_column("Semaine")
        t3.add_column("Montant", justify="right")
        for _, row in wk.iterrows():
            t3.add_row(str(row["period"].date()), f"{row['spend']} €")
        console.print(t3)

    # Budget alerts
    if alerts and BUDGET_FILE.exists():
        budget = load_budget(BUDGET_FILE)
        over = check_alerts(view, budget, month)
        console.print()
        if not over:
            console.print("[green]Aucun dépassement de budget.[/green]")
        else:
            t4 = Table(title="Alertes budget")
            t4.add_column("Catégorie")
            t4.add_column("Dépensé", justify="right")
            t4.add_column("Budget", justify="right")
            t4.add_column("Dépassement", justify="right")
            t4.add_column("%", justify="right")
            for a in over:
                t4.add_row(
                    a["category"],
                    f"[red]{a['spent']} €[/red]",
                    f"{a['budget']} €",
                    f"[red]+{a['over']} €[/red]",
                    f"[red]{a['pct']}%[/red]",
                )
            console.print(t4)


@cli.command()
@click.argument("csv_files", nargs=-1, required=True)
@click.option("--month", default=None, help="Filter by month, e.g. 2026-01")
@click.option("--out", default="data/charts", help="Output folder for charts.")
def charts(csv_files, month, out):
    """Generate PNG charts: net flow, category pie, weekly spend."""
    df = _load(*csv_files)
    view = _filter_month(df, month)
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)

    monthly_net_flow(df, out_dir / "monthly_flow.png")
    console.print(f"[green]✓[/green] {out_dir}/monthly_flow.png")

    category_pie(view, out_dir / "category_pie.png")
    console.print(f"[green]✓[/green] {out_dir}/category_pie.png")

    weekly_spend_bar(view, out_dir / "weekly_spend.png")
    console.print(f"[green]✓[/green] {out_dir}/weekly_spend.png")

    console.print(f"\n[bold]Charts saved to {out_dir}/[/bold]")


if __name__ == "__main__":
    cli()
