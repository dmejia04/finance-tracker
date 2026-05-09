import pandas as pd

# Maps category name → keywords to match in transaction description (case-insensitive)
CATEGORIES: dict[str, list[str]] = {
    # --- Entrées ---
    "salaire":          ["salaire", "paie", "employeur"],
    "primes":           ["prime"],
    "epargne":          ["livret", "epargne", "pel", "cel", "savings", "fortuneo"],
    "mutuelle":         ["mutuelle", "mgen", "alan", "apicil", "henner"],
    "amelie":           ["ameli", "cpam", "securite sociale", "caf "],
    "remboursements":   ["remboursement", "remb "],
    "vinted":           ["vinted"],

    # --- Charges Fixes ---
    "loyer":            ["loyer", "loyement", "logement", "bail"],
    "pret_voiture":     ["credit auto", "pret auto", "pret voiture", "loa ", "pret voitire", "sofinco"],
    "pret_revolut":     ["ravolut", "revolut"],
    "pret_provisio":    ["provisio"],
    "edf":              ["edf", "engie", "electricite", "gaz reseau"],
    "frais_bancaires":  ["frais bancaires", "cotisation carte", "frais tenue", "commission"],
    "assurance_voiture":["assurance auto", "maaf", "axa auto", "macif", "matmut"],
    "assurance_habitat":["assurance hab", "assurance logement", "assurance maison", "cardif iard"],
    "assurance_nomade": ["assurance nomade", "assurance telephone", "assurance mobile"],
    "internet":         ["orange", "sfr", "bouygues", "free ", "bbox", "fibre", "adsl"],
    "telephone":        ["forfait mobile", "forfait tel", "red by sfr", "sosh", "b&you"],
    "apple":            ["apple"],
    "amazon_prime":     ["amazon prime", "amazon.fr"],
    "spotify":          ["spotify"],
    "natgeo":           ["national geo", "natgeo", "disney+", "disney plus"],

    # --- Charges Variables ---
    "courses":          ["carrefour", "leclerc", "intermarche", "lidl", "aldi",
                         "monoprix", "franprix", "super u", "auchan", "casino supermarche"],
    "livraisons":       ["uber eats", "deliveroo", "just eat", "dominos", "frichti"],
    "cantine":          ["cantine", "resto u ", "restaurant administratif"],
    "restos":           ["restaurant", "brasserie", "bistrot", "pizzeria", "sushi",
                         "burger", "mcdonald", "kfc", "subway"],
    "bars":             ["bar ", "pub ", "biere", "cocktail", "cafe de"],
    "vin":              ["cave ", "vins ", "wine", "nicolas "],
    "weekends":         ["voyage", "berlin", "wero "],
    "maison":           ["ikea", "bricomarche", "leroy merlin", "castorama", "brico depot",
                         "maison du monde"],
    "vetements":        ["zara", "h&m", "uniqlo", "pull and bear", "mango", "kiabi",
                         "asos", "zalando"],
    "sport":            ["decathlon", "intersport", "trail", "course a pied", "running"],
    "tech":             ["fnac", "darty", "boulanger", "ldlc", "materiel.net"],
    "loisirs":          ["cinema", "theatre", "musee", "escape", "bowling", "paintball"],
    "cadeaux":          ["cadeau", "fleurs", "florist"],
    "essence":          ["total ", "bp ", "shell ", "esso", "essence", "carburant", "station"],
    "peages":           ["sanef", "vinci autoroute", "peage", "telepeage", "liber-t", "autoroutes du sud"],
    "transport":        ["sncf", "ratp", "navigo", "blablacar", "ouibus", "flixbus",
                         "uber ", "taxi", "vtc "],
    "strava":           ["strava"],
    "velotoulouse":     ["velotoulouse", "velo toulouse", "veltoul"],
    "amex":             ["american express", "amex"],
    "online_shopping":  ["paypal", "oney"],
    "divers":           [],  # catch-all — always last
}

# Which categories count as income (used to split in/out)
INCOME_CATEGORIES = {"salaire", "primes", "epargne", "mutuelle", "amelie", "remboursements", "vinted"}

# Group labels for reporting
FIXED_CHARGES = {
    "loyer", "pret_voiture", "pret_revolut", "pret_provisio", "edf",
    "frais_bancaires", "assurance_voiture", "assurance_habitat", "assurance_nomade",
    "internet", "telephone", "apple", "amazon_prime", "spotify", "natgeo",
}
VARIABLE_CHARGES = {
    "courses", "livraisons", "cantine", "restos", "bars", "vin", "maison",
    "vetements", "sport", "tech", "loisirs", "cadeaux", "essence", "peages",
    "transport", "strava", "velotoulouse", "amex", "online_shopping", "divers",
}


def load_transactions(raw: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(raw)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if "direction" not in df.columns and "amount" in df.columns:
        df["direction"] = df["amount"].apply(lambda x: "in" if x > 0 else "out")
        df["amount_abs"] = df["amount"].abs()

    # classify using both name and short_label if available
    text_col = df.get("name", pd.Series([""] * len(df))).astype(str)
    if "short_label" in df.columns:
        text_col = text_col + " " + df["short_label"].astype(str)

    df["category"] = text_col.apply(_classify)

    df["group"] = df["category"].apply(
        lambda c: "entrees" if c in INCOME_CATEGORIES
        else "charges_fixes" if c in FIXED_CHARGES
        else "charges_variables"
    )

    cols = ["date", "name", "amount", "amount_abs", "direction", "category", "group"]
    return df[[c for c in cols if c in df.columns]]


def _classify(text: str) -> str:
    text = str(text).lower()
    for category, keywords in CATEGORIES.items():
        if keywords and any(k in text for k in keywords):
            return category
    return "divers"
