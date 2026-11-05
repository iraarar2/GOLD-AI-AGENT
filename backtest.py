
import pandas as pd


# GOLD backtest settings
SYMBOL = "XAUUSDm"
EMA_FAST = 8
EMA_MID = 21
EMA_TREND = 125

STOP_LOSS = 3.0
TAKE_PROFIT = 6.0
INITIAL_BALANCE = 100.0


def run_backtest(file_name="gold_data.csv"):

    df = pd.read_csv(file_name)

    required = ["open", "high", "low", "close"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    df = df.dropna(subset=required).reset_index(drop=True)

    df["ema8"] = df["close"].ewm(
        span=EMA_FAST, adjust=False
    ).mean()

    df["ema21"] = df["close"].ewm(
        span=EMA_MID, adjust=False
    ).mean()

    df["ema125"] = df["close"].ewm(
        span=EMA_TREND, adjust=False
    ).mean()

    df["signal"] = "NO TRADE"

    buy = (
        (df["ema8"] > df["ema21"]) &
        (df["close"] > df["ema125"])
    )

    sell = (
        (df["ema8"] < df["ema21"]) &
        (df["close"] < df["ema125"])
    )

    df.loc[buy, "signal"] = "BUY"
    df.loc[sell, "signal"] = "SELL"

    trades = []
    balance = INITIAL_BALANCE
    position = None

    for i in range(125, len(df)):

        row = df.iloc[i]

        # Check existing trade first
        if position is not None:

            if position["type"] == "BUY":
                hit_sl = row["low"] <= position["sl"]
                hit_tp = row["high"] >= position["tp"]

            else:
                hit_sl = row["high"] >= position["sl"]
                hit_tp = row["low"] <= position["tp"]

            # Conservative assumption if both hit
            if hit_sl or hit_tp:

                if hit_sl:
                    exit_price = position["sl"]
                    result = "LOSS"
                else:
                    exit_price = position["tp"]
                    result = "WIN"

                if position["type"] == "BUY":
                    pnl = exit_price - position["entry"]
                else:
                    pnl = position["entry"] - exit_price

                balance += pnl

                trades.append({
                    "type": position["type"],
                    "entry": position["entry"],
                    "exit": exit_price,
                    "pnl": pnl,
                    "result": result,
                    "balance": balance
                })

                position = None

        # Signal from previous candle, entry at current open
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

    # Close any remaining position at final candle close
    if position is not None:
        exit_price = float(df.iloc[-1]["close"])

        if position["type"] == "BUY":
            pnl = exit_price - position["entry"]
        else:
            pnl = position["entry"] - exit_price

        balance += pnl

        trades.append({
            "type": position["type"],
            "entry": position["entry"],
            "exit": exit_price,
            "pnl": pnl,
            "result": "WIN" if pnl > 0 else "LOSS",
            "balance": balance
        })

    results = pd.DataFrame(trades)

    if results.empty:
        print("No trades found.")
        return results

    wins = (results["pnl"] > 0).sum()
    losses = (results["pnl"] <= 0).sum()
    win_rate = wins / len(results) * 100

    results["peak"] = results["balance"].cummax()
    results["drawdown"] = (
        results["peak"] - results["balance"]
    )

    print("\n===== GOLD AI BACKTEST =====")
    print("Symbol:", SYMBOL)
    print("Initial balance:", INITIAL_BALANCE)
    print("Total trades:", len(results))
    print("Wins:", wins)
    print("Losses:", losses)
    print("Win rate:", round(win_rate, 2), "%")
    print("Net P/L:", round(results["pnl"].sum(), 2))
    print("Final balance:", round(balance, 2))
    print(
        "Max drawdown:",
        round(results["drawdown"].max(), 2)
    )

    results.to_csv("backtest_results.csv", index=False)

    print("\nResults saved to backtest_results.csv")

    return results


if __name__ == "__main__":
    run_backtest()
