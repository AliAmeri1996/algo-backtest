import pandas as pd
import numpy as np


def calculate_metrics(df: pd.DataFrame, initial_capital: float = 10_000.0) -> dict:
    """
    Calculates key performance metrics from a completed backtest.
    """
    portfolio = df["Portfolio_Value"]
    daily_returns = df["Daily_Return"].dropna()

    # Total return
    total_return = (portfolio.iloc[-1] - initial_capital) / initial_capital

    # Annualised return (CAGR)
    n_years = len(df) / 252
    cagr = (portfolio.iloc[-1] / initial_capital) ** (1 / n_years) - 1

    # Sharpe ratio (assumes risk-free rate of 0 for simplicity)
    sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)

    # Max drawdown
    max_drawdown = df["Drawdown"].min()

    # Trade stats
    trades = df[df["Trade"] == 1].index  # buy signals = number of trades entered
    n_trades = len(trades)

    # Win rate — a trade is a win if the sell price > buy price
    wins = 0
    buy_price = None

    for i, row in df.iterrows():
        trade = row["Trade"].item()
        price = row["Close"].item()

        if trade == 1:
            buy_price = price
        elif trade == -1 and buy_price is not None:
            if price > buy_price:
                wins += 1
            buy_price = None

    n_sells = len(df[df["Trade"] == -1])
    win_rate = wins / n_sells if n_sells > 0 else 0

    return {
        "Total Return": f"{total_return:.2%}",
        "CAGR": f"{cagr:.2%}",
        "Sharpe Ratio": f"{sharpe:.2f}",
        "Max Drawdown": f"{max_drawdown:.2%}",
        "Number of Trades": n_trades,
        "Win Rate": f"{win_rate:.2%}",
    }




if __name__ == "__main__":
    from data import fetch_price_data
    from strategy import moving_average_crossover
    from backtester import run_backtest

    df = fetch_price_data("SPY", "2010-01-01", "2024-01-01")
    df = moving_average_crossover(df)
    df = run_backtest(df)

    metrics = calculate_metrics(df)
    print("\n--- SPY Backtest Results ---")
    for k, v in metrics.items():
        print(f"{k:20s}: {v}")