import tomllib
from pathlib import Path
import pandas as pd


def load_budget(path: Path) -> dict[str, float]:
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return {k: float(v) for k, v in data.get("budget", {}).items()}


def check_alerts(df: pd.DataFrame, budget: dict[str, float], month: str | None = None) -> list[dict]:
    out = df[df["direction"] == "out"].copy()

    if month:
        out = out[out["date"].dt.to_period("M").astype(str) == month]

    spent = out.groupby("category")["amount_abs"].sum()
    alerts = []
    for category, limit in budget.items():
        total = spent.get(category, 0.0)
        if total > limit:
            alerts.append({
                "category": category,
                "spent": round(total, 2),
                "budget": limit,
                "over": round(total - limit, 2),
                "pct": round((total / limit) * 100),
            })

    return sorted(alerts, key=lambda a: a["over"], reverse=True)
