import pandas as pd
import numpy as np


def run_backtest(df: pd.DataFrame, initial_capital: float = 10_000.0) -> pd.DataFrame:
    """
    Simulates trading based on signals in df.
    Returns df with portfolio value tracked over time.
    No transaction costs (noted as a limitation).
    """
    df = df.copy()

    cash = initial_capital
    shares = 0
    portfolio_values = []

    for i, row in df.iterrows():
        price = row["Close"].item()
        trade = row["Trade"].item()

        # Buy signal — go all in
        if trade == 1 and cash > 0:
            shares = cash / price
            cash = 0

        # Sell signal — exit position
        elif trade == -1 and shares > 0:
            cash = shares * price
            shares = 0

        # Portfolio value = cash + value of any held shares
        portfolio_value = cash + (shares * price)
        portfolio_values.append(portfolio_value)

    df["Portfolio_Value"] = portfolio_values

    # Daily returns
    df["Daily_Return"] = df["Portfolio_Value"].pct_change()

    # Drawdown
    df["Peak"] = df["Portfolio_Value"].cummax()
    df["Drawdown"] = (df["Portfolio_Value"] - df["Peak"]) / df["Peak"]

    return df




