import pandas as pd


def moving_average_crossover(df: pd.DataFrame, short_window: int = 50, long_window: int = 200) -> pd.DataFrame:
    """
    Generates buy/sell signals based on MA crossover.
    
    Signal = 1  → hold (we're in a long position)
    Signal = 0  → out of market
    """
    df = df.copy()

    df["MA_short"] = df["Close"].rolling(window=short_window).mean()
    df["MA_long"] = df["Close"].rolling(window=long_window).mean()

    # 1 when short MA is above long MA, 0 otherwise
    df["Signal"] = 0
    df.loc[df["MA_short"] > df["MA_long"], "Signal"] = 1

    # Trade column: +1 = buy, -1 = sell, 0 = hold
    df["Trade"] = df["Signal"].diff()

    # Drop rows before long MA has enough data
    df.dropna(inplace=True)

    return df

#test


if __name__ == "__main__":
    from data import fetch_price_data

    df = fetch_price_data("SPY", "2010-01-01", "2024-01-01")
    df = moving_average_crossover(df)

    buys = df[df["Trade"] == 1]
    sells = df[df["Trade"] == -1]

    print(f"Buy signals:  {len(buys)}")
    print(f"Sell signals: {len(sells)}")
    print(df[["Close", "MA_short", "MA_long", "Signal", "Trade"]].tail(10))