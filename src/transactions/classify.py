import pandas as pd

CATEGORY_MAP = {
    "Food and Drink": "food",
    "Shops": "shopping",
    "Travel": "travel",
    "Recreation": "entertainment",
    "Healthcare": "health",
    "Service": "services",
    "Transfer": "transfer",
    "Payment": "payment",
    "Bank Fees": "fees",
}


def load_transactions(raw: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(raw)
    df["date"] = pd.to_datetime(df["date"])
    # Plaid amounts: positive = debit (money out), negative = credit (money in)
    df["direction"] = df["amount"].apply(lambda x: "out" if x > 0 else "in")
    df["amount_abs"] = df["amount"].abs()
    df["category_label"] = df["category"].apply(_map_category)
    return df[["date", "name", "amount", "amount_abs", "direction", "category_label", "merchant_name"]]


def _map_category(cats: list | None) -> str:
    if not cats:
        return "other"
    top = cats[0] if cats else ""
    return CATEGORY_MAP.get(top, "other")
