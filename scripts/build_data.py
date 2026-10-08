"""Seçili hisseler için backtest sonuçlarını hesaplayıp docs/data/results.json dosyasına yazar.

Sitede ham fiyat YOK; sadece hesaplanmış portföy eğrisi (haftalık örneklenmiş) ve istatistikler yayınlanır.
GitHub Actions bu scripti her iş günü çalıştırır. Elle çalıştırmak için:

    python scripts/build_data.py
"""
import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd
import yfinance as yf

TICKERS = {
    # ETF'ler
    "SPY": "S&P 500 ETF",
    "VOO": "Vanguard S&P 500 ETF",
    "QQQ": "Nasdaq 100 ETF",
    "VTI": "Vanguard Toplam ABD Borsası ETF",
    "DIA": "Dow Jones ETF",
    "IWM": "Russell 2000 (küçük şirketler) ETF",
    # Teknoloji
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "GOOGL": "Alphabet (Google)",
    "AMZN": "Amazon",
    "META": "Meta",
    "TSLA": "Tesla",
    "AVGO": "Broadcom",
    "AMD": "AMD",
    "NFLX": "Netflix",
    "INTC": "Intel",
    "ORCL": "Oracle",
    "CRM": "Salesforce",
    "ADBE": "Adobe",
    "PLTR": "Palantir",
    "UBER": "Uber",
    # Finans
    "JPM": "JPMorgan Chase",
    "V": "Visa",
    "MA": "Mastercard",
    "BAC": "Bank of America",
    # Tüketim
    "WMT": "Walmart",
    "COST": "Costco",
    "KO": "Coca-Cola",
    "PEP": "PepsiCo",
    "MCD": "McDonald's",
    "NKE": "Nike",
    "DIS": "Disney",
    "PG": "Procter & Gamble",
    # Sağlık, enerji, sanayi
    "JNJ": "Johnson & Johnson",
    "UNH": "UnitedHealth",
    "PFE": "Pfizer",
    "XOM": "Exxon Mobil",
    "BA": "Boeing",
}
FETCH_START = "2005-01-01"
FAST, SLOW = 50, 200
COST = 0.001  # her alım/satımda %0,1 (komisyon + spread + kur farkı varsayımı)
BASE = 1000.0
PERIOD_LABELS = {"ytd": "Yıl başından beri", "1y": "Son 1 yıl", "3y": "Son 3 yıl", "5y": "Son 5 yıl", "10y": "Son 10 yıl", "max": "En uzun dönem"}
OUT = Path(__file__).resolve().parent.parent / "docs" / "data" / "results.json"


def load_close(symbol: str) -> pd.Series:
    df = yf.download(symbol, start=FETCH_START, auto_adjust=True, progress=False)
    if df.empty:
        raise RuntimeError(f"{symbol} için veri indirilemedi")
    return df["Close"].squeeze().dropna()


def period_start(period: str, close: pd.Series):
    """Dönemin başlangıç gününü döndürür. SMA için gereken ısınma verisi yoksa None."""
    last = close.index[-1]
    if period == "max":
        cutoff = close.index[SLOW]
    elif period == "ytd":
        cutoff = pd.Timestamp(year=last.year, month=1, day=1)
    else:
        cutoff = last - pd.DateOffset(years=int(period[:-1]))
    if cutoff < close.index[SLOW]:
        return None
    return close.index[close.index >= cutoff][0]


def stats(equity: pd.Series, position_changes: int) -> dict:
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    total = equity.iloc[-1] / BASE - 1
    cagr = (equity.iloc[-1] / BASE) ** (1 / years) - 1 if years >= 1 else None
    drawdown = (equity / equity.cummax() - 1).min()
    return {
        "final": round(float(equity.iloc[-1]), 2),
        "total_return": round(float(total), 4),
        "cagr": None if cagr is None else round(float(cagr), 4),
        "max_drawdown": round(float(drawdown), 4),
        "trades": int(position_changes),
    }


def sample(series: pd.Series) -> list:
    """Dosya küçük kalsın diye her 5. gün + son gün."""
    idx = list(range(0, len(series), 5))
    if idx[-1] != len(series) - 1:
        idx.append(len(series) - 1)
    return idx


def build_ticker(close: pd.Series) -> dict:
    daily = close.pct_change().fillna(0)
    position = (close.rolling(FAST).mean() > close.rolling(SLOW).mean()).astype(int).shift(1).fillna(0)
    trade_cost = position.diff().abs().fillna(0) * COST
    strat = position * daily - trade_cost

    periods = {}
    for key, label in PERIOD_LABELS.items():
        start = period_start(key, close)
        if start is None:
            continue
        bh_r = daily.loc[start:].copy()
        sma_r = strat.loc[start:].copy()
        pos = position.loc[start:]
        bh_r.iloc[0] = -COST  # dönem başında alım maliyeti
        sma_r.iloc[0] = -COST * pos.iloc[0]
        bh_eq = BASE * (1 + bh_r).cumprod()
        sma_eq = BASE * (1 + sma_r).cumprod()
        idx = sample(bh_eq)
        periods[key] = {
            "label": label,
            "start": bh_eq.index[0].strftime("%Y-%m-%d"),
            "end": bh_eq.index[-1].strftime("%Y-%m-%d"),
            "dates": [bh_eq.index[i].strftime("%Y-%m-%d") for i in idx],
            "bh": [round(float(bh_eq.iloc[i]), 2) for i in idx],
            "sma": [round(float(sma_eq.iloc[i]), 2) for i in idx],
            "stats": {
                "bh": stats(bh_eq, 1),
                "sma": stats(sma_eq, int(pos.diff().abs().iloc[1:].sum()) + int(pos.iloc[0])),
            },
        }
    return periods


def main() -> None:
    out = {
        "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
        "base": BASE,
        "cost": COST,
        "fast": FAST,
        "slow": SLOW,
        "tickers": {},
    }
    for symbol, name in TICKERS.items():
        try:
            close = load_close(symbol)
        except Exception as exc:  # tek hisse hata verse de diğerleri yazılsın
            print(f"UYARI: {symbol} atlandı: {exc}", file=sys.stderr)
            continue
        out["tickers"][symbol] = {"name": name, "last_date": close.index[-1].strftime("%Y-%m-%d"), "periods": build_ticker(close)}
        print(f"{symbol}: tamam")
    if not out["tickers"]:
        sys.exit("Hiç veri alınamadı, dosya değiştirilmedi.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Yazıldı: {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
