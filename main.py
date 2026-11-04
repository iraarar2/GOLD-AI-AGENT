from dataclasses import dataclass
from typing import Literal


@dataclass
class MarketAnalysis:
    h4: str
    h1: str
    m15: str
    m5: str
    m3: str
    spread_ok: bool
    volatility_ok: bool


@dataclass
class Decision:
    action: Literal["BUY", "SELL", "NO_TRADE"]
    score: int
    reason: str


def analyze_market(data: MarketAnalysis) -> Decision:

    if not data.spread_ok:
        return Decision("NO_TRADE", 0, "Spread terlalu tinggi")

    if not data.volatility_ok:
        return Decision("NO_TRADE", 0, "Volatilitas tidak sesuai")

    timeframes = [
        data.h4,
        data.h1,
        data.m15,
        data.m5,
        data.m3
    ]

    buy_score = sum(x == "BULLISH" for x in timeframes)
    sell_score = sum(x == "BEARISH" for x in timeframes)

    if buy_score >= 4 and data.m3 == "BULLISH":
        return Decision("BUY", buy_score, "Konfirmasi bullish")

    if sell_score >= 4 and data.m3 == "BEARISH":
        return Decision("SELL", sell_score, "Konfirmasi bearish")

    return Decision("NO_TRADE", max(buy_score, sell_score),
                    "Konfirmasi belum cukup")


if __name__ == "__main__":
    print("GOLD AI AGENT initialized")
    print("Trading instrument: XAUUSDm")
    print("Strategy: ICT/SMC Hybrid")
    print("Mode: Analysis only")
