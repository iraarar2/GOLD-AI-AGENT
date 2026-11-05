
import pandas as pd
from strategy import add_ema_columns


# BACKTEST CONFIGURATION
SYMBOL = "XAUUSDm"

STOP_LOSS = 3.0
TAKE_PROFIT = 6.0

SPREAD_PRICE = 0.0

DATA_FILE = "gold_data.csv"


def run_backtest():

    df = pd.read_csv(DATA_FILE)

    required = ["open", "high", "low", "close"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=required).reset_index(drop=True)

    if len(df) < 130:
        raise ValueError("Not enough historical candles")

    # Use the same EMA engine as the main strategy
    df = add_ema_columns(df)

    buy = (
        (df["ema8"] > df["ema21"]) &
        (df["close"] > df["ema125"])
    )

    sell = (
        (df["ema8"] < df["ema21"]) &
        (df["close"] < df["ema125"])
    )

    df["signal"] = "NO_TRADE"
    df.loc[buy, "signal"] = "BUY"
    df.loc[sell, "signal"] = "SELL"

    trades = []
    position = None

    for i in range(125, len(df)):

        row = df.iloc[i]

        # Manage an existing position
        if position is not None:

            if position["type"] == "BUY":
                hit_sl = row["low"] <= position["sl"]
                hit_tp = row["high"] >= position["tp"]
            else:
                hit_sl = row["high"] >= position["sl"]
                hit_tp = row["low"] <= position["tp"]

            # Conservative assumption:
            # if SL and TP hit in the same candle, count SL first.
            if hit_sl or hit_tp:

                if hit_sl:
                    exit_price = position["sl"]
                    result = "LOSS"
                else:
                    exit_price = position["tp"]
                    result = "WIN"

                if position["type"] == "BUY":
                    gross = exit_price - position["entry"]
                else:
                    gross = position["entry"] - exit_price

                pnl = gross - SPREAD_PRICE

                trades.append({
                    "type": position["type"],
                    "entry": position["entry"],
                    "exit": exit_price,
                    "pnl_price": pnl,
                    "result": result
                })

                position = None

        # Enter using the previous candle's signal
        # at the current candle's opening price.
        if position is None and i > 125:

            signal = df.iloc[i - 1]["signal"]
            entry = float(row["open"])

            if signal == "BUY":
                position = {
                    "type": "BUY",
                    "entry": entry,
                    "sl": entry - STOP_LOSS,
                    "tp": entry + TAKE_PROFIT
                }

            elif signal == "SELL":
                position = {
                    "type": "SELL",
                    "entry": entry,
                    "sl": entry + STOP_LOSS,
                    "tp": entry - TAKE_PROFIT
                }

    # Close remaining position at final candle close
    if position is not None:

        exit_price = float(df.iloc[-1]["close"])

        if position["type"] == "BUY":
            gross = exit_price - position["entry"]
        else:
            gross = position["entry"] - exit_price

        pnl = gross - SPREAD_PRICE

        trades.append({
            "type": position["type"],
            "entry": position["entry"],
            "exit": exit_price,
            "pnl_price": pnl,
            "result": "result": "WIN" if pnl > 0 else "LOSS"
        })

    results = pd.DataFrame(trades)

    if results.empty:
        print("No trades generated.")
        return

    results["equity_price"] = results["pnl_price"].cumsum()
    results["peak"] = results["equity_price"].cummax()
    results["drawdown_price"] = (
        results["peak"] - results["equity_price"]
    )

    wins = (results["pnl_price"] > 0).sum()
    losses = (results["pnl_price"] < 0).sum()

    gross_profit = results.loc[
        results["pnl_price"] > 0, "pnl_price"
    ].sum()

    gross_loss = abs(results.loc[
        results["pnl_price"] < 0, "pnl_price"
    ].sum())

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0 else float("inf")
    )

    win_rate = wins / len(results) * 100

    print("\n===== GOLD EMA BACKTEST =====")
    print("Symbol:", SYMBOL)
    print("Strategy: EMA 8 / 21 / 125")
    print("Total trades:", len(results))
    print("Wins:", wins)
    print("Losses:", losses)
    print("Win rate:", round(win_rate, 2), "%")
    print("Net price P/L:", round(results["pnl_price"].sum(), 3))
    print("Profit factor:", round(profit_factor, 2))
    print(
        "Max drawdown (price units):",
        round(results["drawdown_price"].max(), 3)
    )

    results.to_csv("backtest_results.csv", index=False)

    print("\nSaved: backtest_results.csv")

    return results


if __name__ == "__main__":
    run_backtest()
