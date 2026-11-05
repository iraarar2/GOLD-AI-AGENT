
from dataclasses import dataclass
from typing import Literal

from strategy import analyze_gold


@dataclass
class Decision:
    action: Literal["BUY", "SELL", "NO_TRADE"]
    reason: str
    price: float
    ema8: float
    ema21: float
    ema125: float


def analyze_market(candles):

    result = analyze_gold(candles)

    return Decision(
        action=result["signal"],
        reason=result["reason"],
        price=result["price"],
        ema8=result["ema8"],
        ema21=result["ema21"],
        ema125=result["ema125"]
    )


def print_analysis(decision):

    print("\n===== GOLD AI AGENT =====")
    print("Symbol: XAUUSDm")
    print("Strategy: EMA 8 / 21 / 125")

    print("Price:", decision.price)
    print("EMA 8:", decision.ema8)
    print("EMA 21:", decision.ema21)
    print("EMA 125:", decision.ema125)

    print("Decision:", decision.action)
    print("Reason:", decision.reason)


if __name__ == "__main__":

    print("GOLD AI AGENT initialized")
    print("Mode: EMA analysis")
    print("Execution: Disabled")
    print("Waiting for market data...")
