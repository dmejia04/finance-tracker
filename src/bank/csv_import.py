import pandas as pd
from pathlib import Path

# BNP Paribas CSV: no header row for transactions
# cols: date ; short_label ; type ; full_description ; amount
BNP_COLS = ["date", "short_label", "type", "name", "amount"]


def load_csv(path: str | Path) -> list[dict]:
    path = Path(path)
    raw = path.read_bytes()
    encoding = "utf-8-sig" if raw[:3] == b"\xef\xbb\xbf" else "latin-1"

    # skip first line (account summary), no header
    df = pd.read_csv(
        path,
        sep=";",
        encoding=encoding,
        skiprows=1,
        header=None,
        names=BNP_COLS,
    )

    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date"])

    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace("\xa0", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    df["direction"] = df["amount"].apply(lambda x: "in" if x > 0 else "out")
    df["amount_abs"] = df["amount"].abs()

    return df.to_dict(orient="records")
