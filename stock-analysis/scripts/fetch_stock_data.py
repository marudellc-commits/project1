import json
from pathlib import Path
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def load_watchlist():
    path = ROOT / "config" / "watchlist.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_quote(symbol, data):
    path = RAW_DIR / f"{symbol}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_quote(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    history = ticker.history(period="1y")
    history_json = json.loads(history.reset_index().to_json(orient="records", date_format="iso"))
    return {
        "info": info,
        "history": history_json,
    }


def main():
    symbols = load_watchlist()
    for symbol in symbols:
        print(f"fetching {symbol}")
        data = fetch_quote(symbol)
        save_quote(symbol, data)


if __name__ == "__main__":
    main()
