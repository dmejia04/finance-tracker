import pandas as pd
from pathlib import Path

# BNP Paribas CSV export uses ';' delimiter and French date format
BNP_COLUMNS = {
    "Date": "date",
    "Libellé": "name",
    "Montant": "amount",
    "Devise": "currency",
}


def load_csv(path: str | Path) -> list[dict]:
    """Auto-detect delimiter and load bank CSV into standard transaction dicts."""
    path = Path(path)
    raw = path.read_bytes()

    # detect encoding
    encoding = "utf-8-sig" if raw[:3] == b"\xef\xbb\xbf" else "latin-1"

    # try semicolon first (French banks), fall back to comma
    for sep in (";", ","):
        df = pd.read_csv(path, sep=sep, encoding=encoding, thousands=" ")
        if len(df.columns) > 1:
            break

    df = _normalize(df)
    return df.to_dict(orient="records")


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    # rename known BNP columns, keep others as-is
    df = df.rename(columns={k: v for k, v in BNP_COLUMNS.items() if k in df.columns})

    # strip whitespace from column names
    df.columns = [c.strip() for c in df.columns]

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    if "amount" in df.columns:
        df["amount"] = (
            df["amount"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.replace(" ", "", regex=False)
            .astype(float)
        )
        # normalize: negative = money out (expense), positive = money in (income)
        # BNP exports debits as negative already — no flip needed
        df["direction"] = df["amount"].apply(lambda x: "in" if x > 0 else "out")
        df["amount_abs"] = df["amount"].abs()

    return df
