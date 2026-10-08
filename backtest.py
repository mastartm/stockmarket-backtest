"""Basit backtest: Al-ve-tut (buy & hold) ile hareketli ortalama kesişimi (SMA crossover) karşılaştırması.

Kullanım:
    python backtest.py                  # SPY, 2010'dan bugüne, 1000 USD
    python backtest.py AAPL 2015-01-01  # başka sembol / başlangıç tarihi

Eğitim amaçlıdır, yatırım tavsiyesi değildir. Geçmiş performans geleceği garanti etmez.
"""
import sys

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

SYMBOL = sys.argv[1] if len(sys.argv) > 1 else "SPY"
START = sys.argv[2] if len(sys.argv) > 2 else "2010-01-01"
CAPITAL = 1000.0
FAST, SLOW = 50, 200
COST_PER_TRADE = 0.001  # her alım/satımda %0,1 (komisyon + spread + kur farkı varsayımı; Midas'ın gerçek oranıyla değiştir)


def load_prices(symbol: str, start: str) -> pd.Series:
    df = yf.download(symbol, start=start, auto_adjust=True, progress=False)
    if df.empty:
        sys.exit(f"{symbol} için veri indirilemedi.")
    close = df["Close"]
    return close.squeeze().dropna()


def run_sma_strategy(close: pd.Series) -> pd.Series:
    """Hızlı SMA > yavaş SMA ise hissede, değilse nakitte. Sinyal ertesi gün uygulanır (look-ahead yok)."""
    fast = close.rolling(FAST).mean()
    slow = close.rolling(SLOW).mean()
    position = (fast > slow).astype(int).shift(1).fillna(0)
    daily_ret = close.pct_change().fillna(0)
    trades = position.diff().abs().fillna(0)
    strat_ret = position * daily_ret - trades * COST_PER_TRADE
    return strat_ret


def stats(name: str, ret: pd.Series) -> dict:
    equity = CAPITAL * (1 + ret).cumprod()
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    cagr = (equity.iloc[-1] / CAPITAL) ** (1 / years) - 1
    drawdown = equity / equity.cummax() - 1
    return {
        "Strateji": name,
        "Son değer (USD)": round(equity.iloc[-1], 2),
        "Yıllık getiri": f"{cagr:.1%}",
        "En büyük düşüş": f"{drawdown.min():.1%}",
    }, equity


def main() -> None:
    close = load_prices(SYMBOL, START)
    bh_ret = close.pct_change().fillna(0)
    bh_ret.iloc[0] -= COST_PER_TRADE  # tek alım maliyeti
    sma_ret = run_sma_strategy(close)

    bh_stats, bh_eq = stats("Al-ve-tut", bh_ret)
    sma_stats, sma_eq = stats(f"SMA {FAST}/{SLOW}", sma_ret)

    print(f"\n{SYMBOL}  {close.index[0].date()} -> {close.index[-1].date()}  başlangıç: {CAPITAL:.0f} USD")
    print(pd.DataFrame([bh_stats, sma_stats]).to_string(index=False))

    plt.figure(figsize=(10, 5))
    plt.plot(bh_eq, label="Al-ve-tut")
    plt.plot(sma_eq, label=f"SMA {FAST}/{SLOW}")
    plt.title(f"{SYMBOL}: {CAPITAL:.0f} USD başlangıç")
    plt.ylabel("Portföy değeri (USD)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    out = f"sonuc_{SYMBOL}.png"
    plt.savefig(out, dpi=120)
    print(f"Grafik kaydedildi: {out}")


if __name__ == "__main__":
    main()
