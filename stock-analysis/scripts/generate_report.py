import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_rules():
    path = ROOT / "config" / "screening_rules.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_quotes():
    for path in sorted(RAW_DIR.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        yield path.stem, data["info"], data.get("history", [])


def _calc_equity_ratio(debt_to_equity):
    if debt_to_equity is None:
        return None
    try:
        # yfinance returns debtToEquity as a percentage (e.g. 105.3 means D/E = 1.053)
        return 100 / (1 + float(debt_to_equity) / 100)
    except Exception:
        return None


def _calc_ma_deviation(history, window):
    closes = [h["Close"] for h in history if h.get("Close") is not None]
    if len(closes) < window:
        return None
    ma = sum(closes[-window:]) / window
    current = closes[-1]
    return (current - ma) / ma * 100


def build_dataframe(quotes):
    rows = []
    for symbol, info, history in quotes:
        roe = info.get("returnOnEquity")
        dividend_yield = info.get("dividendYield")
        earnings_growth = info.get("earningsGrowth")
        revenue_growth = info.get("revenueGrowth")
        peg_ratio = info.get("pegRatio")
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        fifty_two_week_high = info.get("fiftyTwoWeekHigh")

        dist_from_52w_high = None
        if current_price and fifty_two_week_high:
            dist_from_52w_high = (current_price - fifty_two_week_high) / fifty_two_week_high * 100

        rows.append({
            "symbol": symbol,
            "name": info.get("shortName") or info.get("longName"),
            "trailingPE": info.get("trailingPE"),
            "priceToBook": info.get("priceToBook"),
            "ROE_pct": float(roe) * 100 if roe is not None else None,
            "dividend_yield_pct": float(dividend_yield) * 100 if dividend_yield is not None else None,
            "equity_ratio": _calc_equity_ratio(info.get("debtToEquity")),
            "earnings_growth_pct": float(earnings_growth) * 100 if earnings_growth is not None else None,
            "revenue_growth_pct": float(revenue_growth) * 100 if revenue_growth is not None else None,
            "peg_ratio": float(peg_ratio) if peg_ratio is not None else None,
            "dist_from_52w_high_pct": dist_from_52w_high,
            "ma25_deviation_pct": _calc_ma_deviation(history, 25),
            "ma75_deviation_pct": _calc_ma_deviation(history, 75),
            "marketCap": info.get("marketCap"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
        })

    return pd.DataFrame(rows)


def apply_rules(df, rules):
    screened = df.copy()
    screened = screened[screened["trailingPE"].notna()]
    screened = screened[screened["priceToBook"].notna()]
    screened = screened[screened["ROE_pct"].notna()]

    mask = (
        (screened["trailingPE"] <= rules["PER"]["max"]) &
        (screened["priceToBook"] <= rules["PBR"]["max"]) &
        (screened["ROE_pct"] >= rules["ROE"]["min"]) &
        ((screened["dividend_yield_pct"] >= rules["dividend_yield"]["min"]) | screened["dividend_yield_pct"].isna()) &
        ((screened["equity_ratio"] >= rules["equity_ratio"]["min"]) | screened["equity_ratio"].isna())
    )

    if "earnings_growth" in rules:
        mask &= (
            (screened["earnings_growth_pct"] >= rules["earnings_growth"]["min"]) |
            screened["earnings_growth_pct"].isna()
        )

    if "peg_ratio" in rules:
        mask &= (
            (screened["peg_ratio"] <= rules["peg_ratio"]["max"]) |
            screened["peg_ratio"].isna()
        )

    return screened[mask]


def format_val(val, fmt):
    if val is None:
        return "N/A"
    try:
        f = float(val)
        if f != f:  # NaN check
            return "N/A"
        return fmt.format(f)
    except (TypeError, ValueError):
        return "N/A"


def save_outputs(df, screened, rules):
    summary_path = PROCESSED_DIR / "summary.csv"
    screened_path = PROCESSED_DIR / "screened.csv"
    report_path = REPORTS_DIR / "screening_report.md"
    symbol_path = REPORTS_DIR / "screened_symbols.txt"

    df.to_csv(summary_path, index=False)
    screened.to_csv(screened_path, index=False)

    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Screening Report\n\n")
        f.write(f"**実行日**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**対象銘柄数**: {len(df)}  |  **通過銘柄数**: {len(screened)}\n\n")

        f.write("## スクリーニング条件\n\n")
        f.write("| 指標 | 条件 |\n|---|---|\n")
        f.write(f"| PER | ≤ {rules['PER']['max']}倍 |\n")
        f.write(f"| PBR | ≤ {rules['PBR']['max']}倍 |\n")
        f.write(f"| ROE | ≥ {rules['ROE']['min']}% |\n")
        f.write(f"| 配当利回り | ≥ {rules['dividend_yield']['min']}% |\n")
        f.write(f"| 自己資本比率 | ≥ {rules['equity_ratio']['min']}% |\n")
        if "earnings_growth" in rules:
            f.write(f"| 利益成長率 | ≥ {rules['earnings_growth']['min']}% |\n")
        if "peg_ratio" in rules:
            f.write(f"| PEGレシオ | ≤ {rules['peg_ratio']['max']} |\n")
        f.write("\n")

        f.write("## 通過銘柄\n\n")
        if screened.empty:
            f.write("通過銘柄なし\n\n")
        else:
            f.write("### バリュー指標\n\n")
            f.write("| ティッカー | 銘柄名 | PER | PBR | ROE | 配当利回り | 自己資本比率 | セクター |\n")
            f.write("|---|---|---:|---:|---:|---:|---:|---|\n")
            for _, row in screened.iterrows():
                f.write(
                    f"| {row['symbol']} | {row['name'] or 'N/A'}"
                    f" | {format_val(row['trailingPE'], '{:.1f}x')}"
                    f" | {format_val(row['priceToBook'], '{:.2f}x')}"
                    f" | {format_val(row['ROE_pct'], '{:.1f}%')}"
                    f" | {format_val(row['dividend_yield_pct'], '{:.2f}%')}"
                    f" | {format_val(row['equity_ratio'], '{:.1f}%')}"
                    f" | {row.get('sector') or 'N/A'} |\n"
                )

            f.write("\n### kenmo指標（成長・チャート）\n\n")
            f.write("| ティッカー | 利益成長率 | 売上成長率 | PEGレシオ | 52週高値比 | MA25乖離 | MA75乖離 |\n")
            f.write("|---|---:|---:|---:|---:|---:|---:|\n")
            for _, row in screened.iterrows():
                f.write(
                    f"| {row['symbol']}"
                    f" | {format_val(row['earnings_growth_pct'], '{:+.1f}%')}"
                    f" | {format_val(row['revenue_growth_pct'], '{:+.1f}%')}"
                    f" | {format_val(row['peg_ratio'], '{:.2f}')}"
                    f" | {format_val(row['dist_from_52w_high_pct'], '{:+.1f}%')}"
                    f" | {format_val(row['ma25_deviation_pct'], '{:+.1f}%')}"
                    f" | {format_val(row['ma75_deviation_pct'], '{:+.1f}%')} |\n"
                )
            f.write("\n")

        f.write("## 全銘柄サマリー\n\n")
        f.write("| ティッカー | 銘柄名 | PER | PBR | ROE | 利益成長率 | PEG | MA25乖離 | 通過 |\n")
        f.write("|---|---|---:|---:|---:|---:|---:|---:|:---:|\n")
        passed_symbols = set(screened["symbol"])
        for _, row in df.iterrows():
            mark = "✓" if row["symbol"] in passed_symbols else "✗"
            f.write(
                f"| {row['symbol']} | {row['name'] or 'N/A'}"
                f" | {format_val(row['trailingPE'], '{:.1f}x')}"
                f" | {format_val(row['priceToBook'], '{:.2f}x')}"
                f" | {format_val(row['ROE_pct'], '{:.1f}%')}"
                f" | {format_val(row['earnings_growth_pct'], '{:+.1f}%')}"
                f" | {format_val(row['peg_ratio'], '{:.2f}')}"
                f" | {format_val(row['ma25_deviation_pct'], '{:+.1f}%')}"
                f" | {mark} |\n"
            )

    with symbol_path.open("w", encoding="utf-8") as f:
        for symbol in screened["symbol"]:
            f.write(f"{symbol}\n")

    print(f"summary saved to {summary_path}")
    print(f"screened data saved to {screened_path}")
    print(f"report saved to {report_path}")
    print(f"symbols saved to {symbol_path}")


def main():
    rules = load_rules()
    df = build_dataframe(load_quotes())
    screened = apply_rules(df, rules)
    save_outputs(df, screened, rules)


if __name__ == "__main__":
    main()
