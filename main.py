import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data import fetch_price_data
from strategy import moving_average_crossover
from backtester import run_backtest
from metrics import calculate_metrics
from visualisation import plot_results

TICKERS = ["SPY", "AAPL", "MSFT"]
START = "2010-01-01"
END = "2024-01-01"
INITIAL_CAPITAL = 10_000.0
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def run(ticker: str) -> None:
    print(f"\n{'='*40}")
    print(f"  {ticker}")
    print(f"{'='*40}")

    df = fetch_price_data(ticker, START, END)
    df = moving_average_crossover(df)
    df = run_backtest(df, initial_capital=INITIAL_CAPITAL)

    metrics = calculate_metrics(df, initial_capital=INITIAL_CAPITAL)
    for k, v in metrics.items():
        print(f"  {k:20s}: {v}")

    plot_results(df, ticker, output_dir=RESULTS_DIR)


if __name__ == "__main__":
    for ticker in TICKERS:
        run(ticker)

    print(f"\nDone. Charts saved to {RESULTS_DIR}")