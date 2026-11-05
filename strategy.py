
def calculate_ema(prices, period):
    if len(prices) < period:
        return None

    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period

    for price in prices[period:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))

    return ema


def analyze_gold(candles):
    """
    candles: list of dictionaries containing closing prices.
    Example: [{"close": 3900.0}, ...]
    """

    if len(candles) < 125:
        return {
            "signal": "NO TRADE",
            "reason": "Insufficient candle data"
        }

    closes = [float(candle["close"]) for candle in candles]

    ema8 = calculate_ema(closes, 8)
    ema21 = calculate_ema(closes, 21)
    ema125 = calculate_ema(closes, 125)

    price = closes[-1]

    signal = "NO TRADE"
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
