import os
import sys
import streamlit as st
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data import fetch_price_data
from strategy import moving_average_crossover
from backtester import run_backtest
from metrics import calculate_metrics
from visualisation import plot_results

st.set_page_config(page_title="Algo Backtest Engine", layout="wide")

st.title("Algorithmic Trading Backtester")
st.markdown("**Strategy:** Golden Cross — 50/200-day moving average crossover")

# --- Sidebar ---
st.sidebar.header("Parameters")
ticker = st.sidebar.text_input("Ticker", value="SPY").upper()
start_date = st.sidebar.date_input("Start Date", value=None, min_value=None)
end_date = st.sidebar.date_input("End Date", value=None)
short_window = st.sidebar.slider("Short MA (days)", min_value=10, max_value=100, value=50, step=5)
long_window = st.sidebar.slider("Long MA (days)", min_value=50, max_value=300, value=200, step=10)
initial_capital = st.sidebar.number_input("Initial Capital ($)", value=10000, step=1000)

run_button = st.sidebar.button("Run Backtest", type="primary")

if run_button:
    with st.spinner(f"Running backtest for {ticker}..."):
        try:
            df = fetch_price_data(ticker, str(start_date), str(end_date))
            df = moving_average_crossover(df, short_window=short_window, long_window=long_window)
            df = run_backtest(df, initial_capital=float(initial_capital))
            metrics = calculate_metrics(df, initial_capital=float(initial_capital))

            # --- Metrics row ---
            st.subheader(f"Results — {ticker}")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric("Total Return", metrics["Total Return"])
            col2.metric("CAGR", metrics["CAGR"])
            col3.metric("Sharpe Ratio", metrics["Sharpe Ratio"])
            col4.metric("Max Drawdown", metrics["Max Drawdown"])
            col5.metric("Trades", metrics["Number of Trades"])
            col6.metric("Win Rate", metrics["Win Rate"])

            # --- Charts ---
            buys = df[df["Trade"] == 1]
            sells = df[df["Trade"] == -1]

            # Price chart
            st.subheader("Price + Moving Averages")
            fig1, ax1 = plt.subplots(figsize=(14, 4))
            ax1.plot(df.index, df["Close"], color="black", linewidth=1, label="Close")
            ax1.plot(df.index, df["MA_short"], color="blue", linewidth=1, linestyle="--", label=f"{short_window}-day MA")
            ax1.plot(df.index, df["MA_long"], color="red", linewidth=1, linestyle="--", label=f"{long_window}-day MA")
            ax1.scatter(buys.index, buys["Close"], marker="^", color="green", s=100, zorder=5, label="Buy")
            ax1.scatter(sells.index, sells["Close"], marker="v", color="red", s=100, zorder=5, label="Sell")
            ax1.legend(loc="upper left")
            ax1.set_ylabel("Price ($)")
            st.pyplot(fig1)

            # Equity curve
            st.subheader("Equity Curve")
            fig2, ax2 = plt.subplots(figsize=(14, 3))
            ax2.plot(df.index, df["Portfolio_Value"], color="steelblue", linewidth=1.5)
            ax2.set_ylabel("Portfolio Value ($)")
            st.pyplot(fig2)

            # Drawdown
            st.subheader("Drawdown")
            fig3, ax3 = plt.subplots(figsize=(14, 3))
            ax3.fill_between(df.index, df["Drawdown"] * 100, 0, color="red", alpha=0.4)
            ax3.set_ylabel("Drawdown (%)")
            st.pyplot(fig3)

        except Exception as e:
            st.error(f"Error: {e}. Check the ticker and date range.")

else:
    st.info("Set your parameters in the sidebar and click Run Backtest.")