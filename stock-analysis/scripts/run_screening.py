import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_rules():
    path = ROOT / "config" / "screening_rules.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_quote(symbol):
    path = RAW_DIR / f"{symbol}.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def passes_rules(info, rules):
    if info.get("trailingPE") is None:
        return False
    if info.get("priceToBook") is None:
        return False
    if info.get("returnOnEquity") is None:
        return False

    tests = [
        info.get("trailingPE") <= rules["PER"]["max"],
        info.get("priceToBook") <= rules["PBR"]["max"],
        info.get("returnOnEquity") * 100 >= rules["ROE"]["min"],
    ]

    return all(tests)


def main():
    rules = load_rules()
    symbols = [p.stem for p in RAW_DIR.glob("*.json")]
    passed = []

    for symbol in symbols:
        quote = load_quote(symbol)
        info = quote["info"]
        if passes_rules(info, rules):
            passed.append(symbol)

    print("passed:", passed)


if __name__ == "__main__":
    main()
