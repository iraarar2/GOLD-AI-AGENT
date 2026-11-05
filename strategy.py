
import pandas as pd


EMA_FAST = 8
EMA_MID = 21
EMA_TREND = 125


def add_ema_columns(df):
    df = df.copy()

    df["close"] = pd.to_numeric(df["close"])

    df["ema8"] = df["close"].ewm(
        span=EMA_FAST, adjust=False
    ).mean()

    df["ema21"] = df["close"].ewm(
        span=EMA_MID, adjust=False
    ).mean()

    df["ema125"] = df["close"].ewm(
        span=EMA_TREND, adjust=False
    ).mean()

    return df


def analyze_gold(candles):

    if len(candles) < EMA_TREND:
        return {
            "signal": "NO_TRADE",
            "reason": "Insufficient candle data"
        }

    df = pd.DataFrame(candles)
    df = add_ema_columns(df)

    last = df.iloc[-1]

    price = float(last["close"])
    ema8 = float(last["ema8"])
    ema21 = float(last["ema21"])
    ema125 = float(last["ema125"])

    signal = "NO_TRADE"
    reason = "EMA conditions not aligned"

    if ema8 > ema21 and price > ema125:
        signal = "BUY"
        reason = "Bullish EMA alignment"

    elif ema8 < ema21 and price < ema125:
        signal = "SELL"
        reason = "Bearish EMA alignment"

    return {
        "symbol": "XAUUSDm",
        "price": price,
        "ema8": round(ema8, 3),
        "ema21": round(ema21, 3),
        "ema125": round(ema125, 3),
        "signal": signal,
        "reason": reason
    }
