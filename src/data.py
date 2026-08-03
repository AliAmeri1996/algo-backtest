import yfinance as yf
import pandas as pd


def fetch_price_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Download daily OHLCV data for a ticker.
    Returns a clean DataFrame with a DatetimeIndex.
    """
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)

    if df.empty:
        raise ValueError(f"No data returned for {ticker}. Check the ticker or date range.")

    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.index = pd.to_datetime(df.index)
    df.dropna(inplace=True)

    return df




if __name__ == "__main__":
    df = fetch_price_data("SPY", "2010-01-01", "2024-01-01")
    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"Date range: {df.index[0].date()} → {df.index[-1].date()}")