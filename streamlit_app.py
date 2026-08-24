import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

from data import fetch_price_data
from strategy import moving_average_crossover, rsi_strategy, macd_strategy
from backtester import run_backtest
from metrics import calculate_metrics

st.set_page_config(page_title="Algo Backtest Engine", layout="wide")

st.title("Algorithmic Trading Backtester")

# --- Sidebar ---
st.sidebar.header("Parameters")

ticker = st.sidebar.text_input("Ticker", value="SPY").upper()
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2010-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-01-01"))
initial_capital = st.sidebar.number_input("Initial Capital ($)", value=10000, step=1000)

st.sidebar.markdown("---")
strategy = st.sidebar.selectbox("Strategy", [
    "MA Crossover (Golden Cross)",
    "RSI",
    "MACD"
])

# Strategy-specific params
if strategy == "MA Crossover (Golden Cross)":
    st.sidebar.markdown("**MA Parameters**")
    short_window = st.sidebar.slider("Short MA (days)", min_value=10, max_value=100, value=50, step=5)
    long_window = st.sidebar.slider("Long MA (days)", min_value=50, max_value=300, value=200, step=10)

elif strategy == "RSI":
    st.sidebar.markdown("**RSI Parameters**")
    rsi_period = st.sidebar.slider("RSI Period (days)", min_value=5, max_value=30, value=14, step=1)
    oversold = st.sidebar.slider("Oversold threshold", min_value=10, max_value=40, value=30, step=5)
    overbought = st.sidebar.slider("Overbought threshold", min_value=60, max_value=90, value=70, step=5)

elif strategy == "MACD":
    st.sidebar.markdown("**MACD Parameters**")
    fast = st.sidebar.slider("Fast EMA (days)", min_value=5, max_value=20, value=12, step=1)
    slow = st.sidebar.slider("Slow EMA (days)", min_value=20, max_value=50, value=26, step=1)
    signal_window = st.sidebar.slider("Signal Line (days)", min_value=5, max_value=20, value=9, step=1)

run_button = st.sidebar.button("Run Backtest", type="primary")

if run_button:
    with st.spinner(f"Running backtest for {ticker}..."):
        try:
            df = fetch_price_data(ticker, str(start_date), str(end_date))

            if strategy == "MA Crossover (Golden Cross)":
                df = moving_average_crossover(df, short_window=short_window, long_window=long_window)
                strategy_label = f"MA Crossover ({short_window}/{long_window})"

            elif strategy == "RSI":
                df = rsi_strategy(df, period=rsi_period, oversold=oversold, overbought=overbought)
                strategy_label = f"RSI ({rsi_period}, {oversold}/{overbought})"

            elif strategy == "MACD":
                df = macd_strategy(df, fast=fast, slow=slow, signal=signal_window)
                strategy_label = f"MACD ({fast}/{slow}/{signal_window})"

            df = run_backtest(df, initial_capital=float(initial_capital))
            metrics = calculate_metrics(df, initial_capital=float(initial_capital))

            st.subheader(f"Results — {ticker} | {strategy_label}")

            # --- Metrics ---
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric("Total Return", metrics["Total Return"])
            col2.metric("CAGR", metrics["CAGR"])
            col3.metric("Sharpe Ratio", metrics["Sharpe Ratio"])
            col4.metric("Max Drawdown", metrics["Max Drawdown"])
            col5.metric("Trades", metrics["Number of Trades"])
            col6.metric("Win Rate", metrics["Win Rate"])

            buys = df[df["Trade"] == 1]
            sells = df[df["Trade"] == -1]

            # --- Price chart ---
            st.subheader("Price + Signals")
            fig1, ax1 = plt.subplots(figsize=(14, 4))
            ax1.plot(df.index, df["Close"], color="black", linewidth=1, label="Close")

            if strategy == "MA Crossover (Golden Cross)":
                ax1.plot(df.index, df["MA_short"], color="blue", linewidth=1, linestyle="--", label=f"{short_window}-day MA")
                ax1.plot(df.index, df["MA_long"], color="red", linewidth=1, linestyle="--", label=f"{long_window}-day MA")

            ax1.scatter(buys.index, buys["Close"], marker="^", color="green", s=100, zorder=5, label="Buy")
            ax1.scatter(sells.index, sells["Close"], marker="v", color="red", s=100, zorder=5, label="Sell")
            ax1.legend(loc="upper left")
            ax1.set_ylabel("Price ($)")
            st.pyplot(fig1)

            # --- RSI chart ---
            if strategy == "RSI":
                st.subheader("RSI Indicator")
                fig_rsi, ax_rsi = plt.subplots(figsize=(14, 2.5))
                ax_rsi.plot(df.index, df["RSI"], color="purple", linewidth=1)
                ax_rsi.axhline(overbought, color="red", linestyle="--", linewidth=0.8, label=f"Overbought ({overbought})")
                ax_rsi.axhline(oversold, color="green", linestyle="--", linewidth=0.8, label=f"Oversold ({oversold})")
                ax_rsi.fill_between(df.index, df["RSI"], oversold, where=(df["RSI"] < oversold), alpha=0.3, color="green")
                ax_rsi.fill_between(df.index, df["RSI"], overbought, where=(df["RSI"] > overbought), alpha=0.3, color="red")
                ax_rsi.set_ylabel("RSI")
                ax_rsi.legend(loc="upper left")
                st.pyplot(fig_rsi)

            # --- MACD chart ---
            if strategy == "MACD":
                st.subheader("MACD Indicator")
                fig_macd, (ax_m1, ax_m2) = plt.subplots(2, 1, figsize=(14, 4), sharex=True)

                ax_m1.plot(df.index, df["MACD"], color="blue", linewidth=1, label="MACD")
                ax_m1.plot(df.index, df["MACD_Signal"], color="red", linewidth=1, linestyle="--", label="Signal")
                ax_m1.axhline(0, color="black", linewidth=0.5)
                ax_m1.legend(loc="upper left")
                ax_m1.set_ylabel("MACD")

                ax_m2.bar(df.index, df["MACD_Hist"],
                          color=["green" if v >= 0 else "red" for v in df["MACD_Hist"]],
                          alpha=0.6, label="Histogram")
                ax_m2.axhline(0, color="black", linewidth=0.5)
                ax_m2.set_ylabel("Histogram")
                ax_m2.legend(loc="upper left")

                st.pyplot(fig_macd)

            # --- Equity curve ---
            st.subheader("Equity Curve")
            fig2, ax2 = plt.subplots(figsize=(14, 3))
            ax2.plot(df.index, df["Portfolio_Value"], color="steelblue", linewidth=1.5)
            ax2.set_ylabel("Portfolio Value ($)")
            st.pyplot(fig2)

            # --- Drawdown ---
            st.subheader("Drawdown")
            fig3, ax3 = plt.subplots(figsize=(14, 3))
            ax3.fill_between(df.index, df["Drawdown"] * 100, 0, color="red", alpha=0.4)
            ax3.set_ylabel("Drawdown (%)")
            st.pyplot(fig3)

        except Exception as e:
            st.error(f"Error: {e}. Check the ticker and date range.")

else:
    st.info("Set your parameters in the sidebar and click Run Backtest.")