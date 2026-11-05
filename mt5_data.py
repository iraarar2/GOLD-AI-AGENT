
import MetaTrader5 as mt5
import pandas as pd

SYMBOL = "XAUUSDm"
TIMEFRAME = mt5.TIMEFRAME_M15
CANDLE_COUNT = 5000


def get_gold_data():

    if not mt5.initialize():
        print("MT5 connection failed:", mt5.last_error())
        return

    if not mt5.symbol_select(SYMBOL, True):
        print("Symbol unavailable:", SYMBOL)
        mt5.shutdown()
        return

    rates = mt5.copy_rates_from_pos(
        SYMBOL,
        TIMEFRAME,
        0,
        CANDLE_COUNT
    )

    if rates is None or len(rates) == 0:
        print("Historical data unavailable")
        mt5.shutdown()
        return

    df = pd.DataFrame(rates)

    df["time"] = pd.to_datetime(
        df["time"], unit="s"
    )

    df = df.rename(columns={
        "time": "timestamp"
    })

    df = df[
        ["timestamp", "open", "high", "low", "close"]
    ]

    df.to_csv("gold_data.csv", index=False)

    print("GOLD historical data exported")
    print("Total candles:", len(df))

    mt5.shutdown()


if __name__ == "__main__":
    get_gold_data()
