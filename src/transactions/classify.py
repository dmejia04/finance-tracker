import pandas as pd

KEYWORDS = {
    "food": ["restaurant", "cafe", "boulangerie", "supermarché", "carrefour", "lidl", "aldi", "monoprix", "franprix", "sushi", "pizza", "mcdonald", "burger"],
    "transport": ["sncf", "ratp", "navigo", "uber", "taxi", "essence", "total", "bp", "shell"],
    "shopping": ["amazon", "fnac", "zara", "h&m", "decathlon", "ikea", "leboncoin"],
    "health": ["pharmacie", "médecin", "docteur", "clinique", "hopital", "mutuelle"],
    "utilities": ["edf", "engie", "orange", "sfr", "bouygues", "free", "eau", "gaz"],
    "rent": ["loyer", "rent", "bail"],
    "entertainment": ["netflix", "spotify", "cinema", "theatre", "deezer", "canal"],
    "transfer": ["virement", "transfer", "remboursement"],
}


def load_transactions(raw: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(raw)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if "direction" not in df.columns and "amount" in df.columns:
        df["direction"] = df["amount"].apply(lambda x: "in" if x > 0 else "out")
        df["amount_abs"] = df["amount"].abs()

    df["category_label"] = df.get("name", pd.Series([""] * len(df))).apply(_classify)

    cols = ["date", "name", "amount", "amount_abs", "direction", "category_label"]
    return df[[c for c in cols if c in df.columns]]


def _classify(label: str) -> str:
    label_lower = str(label).lower()
    for category, keywords in KEYWORDS.items():
        if any(k in label_lower for k in keywords):
            return category
    return "other"
