import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os


def plot_results(df: pd.DataFrame, ticker: str, output_dir: str = "results") -> None:
    """
    Produces 3 charts:
    1. Price with buy/sell signals + moving averages
    2. Equity curve
    3. Drawdown
    """
    os.makedirs(output_dir, exist_ok=True)

    buys = df[df["Trade"] == 1]
    sells = df[df["Trade"] == -1]

    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    fig.suptitle(f"{ticker} — MA Crossover Backtest", fontsize=14, fontweight="bold")

    # --- Chart 1: Price + signals ---
    ax1 = axes[0]
    ax1.plot(df.index, df["Close"], label="Close", color="black", linewidth=1)
    ax1.plot(df.index, df["MA_short"], label="50-day MA", color="blue", linewidth=1, linestyle="--")
    ax1.plot(df.index, df["MA_long"], label="200-day MA", color="red", linewidth=1, linestyle="--")
    ax1.scatter(buys.index, buys["Close"], marker="^", color="green", zorder=5, label="Buy", s=100)
    ax1.scatter(sells.index, sells["Close"], marker="v", color="red", zorder=5, label="Sell", s=100)
    ax1.set_title("Price + Moving Averages")
    ax1.set_ylabel("Price ($)")
    ax1.legend(loc="upper left")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # --- Chart 2: Equity curve ---
    ax2 = axes[1]
    ax2.plot(df.index, df["Portfolio_Value"], color="steelblue", linewidth=1.5)
    ax2.set_title("Equity Curve")
    ax2.set_ylabel("Portfolio Value ($)")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # --- Chart 3: Drawdown ---
    ax3 = axes[2]
    ax3.fill_between(df.index, df["Drawdown"] * 100, 0, color="red", alpha=0.4)
    ax3.set_title("Drawdown (%)")
    ax3.set_ylabel("Drawdown (%)")
    ax3.set_xlabel("Date")
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    plt.tight_layout()
    output_path = os.path.join(output_dir, f"{ticker}_backtest.png")
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Chart saved → {output_path}")




