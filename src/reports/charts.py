import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from pathlib import Path


def _style():
    plt.rcParams.update({
        "figure.facecolor": "#1e1e2e",
        "axes.facecolor": "#1e1e2e",
        "axes.edgecolor": "#555",
        "axes.labelcolor": "#cdd6f4",
        "xtick.color": "#cdd6f4",
        "ytick.color": "#cdd6f4",
        "text.color": "#cdd6f4",
        "grid.color": "#333",
        "grid.linestyle": "--",
        "grid.alpha": 0.5,
    })


def monthly_net_flow(df: pd.DataFrame, out_path: Path):
    _style()
    monthly = df.copy()
    monthly["month"] = monthly["date"].dt.to_period("M")
    inc = monthly[monthly["direction"] == "in"].groupby("month")["amount_abs"].sum()
    exp = monthly[monthly["direction"] == "out"].groupby("month")["amount_abs"].sum()
    months = sorted(set(inc.index) | set(exp.index))
    labels = [str(m) for m in months]
    x = range(len(months))

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar([i - 0.2 for i in x], [inc.get(m, 0) for m in months], width=0.4, label="Entrées", color="#a6e3a1")
    ax.bar([i + 0.2 for i in x], [exp.get(m, 0) for m in months], width=0.4, label="Sorties", color="#f38ba8")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f} €"))
    ax.set_title("Flux mensuel — Entrées vs Sorties", pad=12)
    ax.legend()
    ax.grid(axis="y")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def category_pie(df: pd.DataFrame, out_path: Path):
    _style()
    out = df[df["direction"] == "out"]
    cats = out.groupby("category")["amount_abs"].sum().sort_values(ascending=False)

    # merge small slices into "autres"
    threshold = cats.sum() * 0.02
    main = cats[cats >= threshold]
    other = cats[cats < threshold].sum()
    if other > 0:
        main["autres"] = other

    colors = plt.cm.Set3.colors[:len(main)]  # type: ignore
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        main.values,
        labels=main.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        pctdistance=0.82,
    )
    for at in autotexts:
        at.set_fontsize(8)
    ax.set_title("Répartition des dépenses par catégorie", pad=16)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def weekly_spend_bar(df: pd.DataFrame, out_path: Path):
    _style()
    out = df[df["direction"] == "out"].copy()
    weekly = out.set_index("date").resample("W")["amount_abs"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(weekly["date"], weekly["amount_abs"], width=5, color="#89b4fa")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f} €"))
    ax.set_title("Dépenses hebdomadaires", pad=12)
    ax.grid(axis="y")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
