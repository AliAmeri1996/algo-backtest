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




def rsi_strategy(df: pd.DataFrame, period: int = 14, oversold: int = 30, overbought: int = 70) -> pd.DataFrame:
    """
    Generates buy/sell signals based on RSI.

    Buy when RSI crosses below oversold threshold (default 30) — stock is oversold, expect bounce.
    Sell when RSI crosses above overbought threshold (default 70) — stock is overbought, expect pullback.
    Between thresholds, hold previous position.
    """
    df = df.copy()

    # Calculate RSI
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Generate signals — stateful (hold position between signals)
    signal = 0
    signals = []

    for rsi_val in df["RSI"]:
        if pd.isna(rsi_val):
            signals.append(0)
            continue
        if rsi_val < oversold:
            signal = 1  # oversold — buy
        elif rsi_val > overbought:
            signal = 0  # overbought — sell
        signals.append(signal)

    df["Signal"] = signals
    df["Trade"] = df["Signal"].diff()
    df.dropna(inplace=True)

    return df