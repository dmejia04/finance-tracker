import pandas as pd


def net_flow(df: pd.DataFrame) -> dict:
    income = df.loc[df["direction"] == "in", "amount_abs"].sum()
    expenses = df.loc[df["direction"] == "out", "amount_abs"].sum()
    return {"income": round(income, 2), "expenses": round(expenses, 2), "net": round(income - expenses, 2)}


def by_category(df: pd.DataFrame) -> pd.DataFrame:
    out = df[df["direction"] == "out"]
    return (
        out.groupby("category_label")["amount_abs"]
        .agg(total="sum", count="count")
        .sort_values("total", ascending=False)
        .round(2)
    )


def concurrent_expenses(df: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
    """Rolling spend grouped by period (default: weekly)."""
    out = df[df["direction"] == "out"].copy()
    out = out.set_index("date").resample(freq)["amount_abs"].sum().reset_index()
    out.columns = ["period", "spend"]
    out["spend"] = out["spend"].round(2)
    return out
