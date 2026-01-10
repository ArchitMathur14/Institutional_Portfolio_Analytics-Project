import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import yfinance as yf

from portfolio.clients import clients
from portfolio.optimizer import optimize_portfolio
from analysis.performance import calculate_portfolio_performance

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Institutional Portfolio Analytics",
    layout="centered"
)

st.title("📊 Institutional Portfolio Analytics Dashboard")

st.write(
    """
    This dashboard simulates portfolio construction for institutional investors
    such as Defined Contribution (DC), Defined Benefit (DB), and Endowment clients.
    Portfolio allocations are generated using current market data and
    mean–variance optimization.
    """
)

# ---------------- Client Selection ----------------
client_key = st.selectbox(
    "Select Client Type",
    options=list(clients.keys())
)

client = clients[client_key]

st.subheader(client["name"])
st.write(f"**Risk Profile:** {client['risk_profile']}")

# ---------------- Load Market Data ----------------
@st.cache_data
def load_market_data():
    tickers = ["SPY", "AGG", "VEA", "GLD"]
    data = yf.download(tickers, start="2019-01-01")["Adj Close"]
    return data.dropna()

prices = load_market_data()

# ---------------- Portfolio Optimization ----------------
weights, _ = optimize_portfolio(prices, client["target_allocation"])
performance = calculate_portfolio_performance(prices, weights)

# ---------------- Display Portfolio Weights ----------------
st.subheader("📌 Recommended Portfolio Allocation")

weights_df = pd.DataFrame.from_dict(weights, orient="index", columns=["Weight"])
weights_df["Weight (%)"] = weights_df["Weight"] * 100
weights_df = weights_df[["Weight (%)"]]

st.bar_chart(weights_df)

# ---------------- Performance Metrics ----------------
st.subheader("📈 Portfolio Performance Metrics")

col1, col2 = st.columns(2)

with col1:
    st.metric("Expected Annual Return", f"{performance['Annual Return']*100:.2f}%")
    st.metric("Sharpe Ratio", f"{performance['Sharpe Ratio']:.2f}")

with col2:
    st.metric("Volatility", f"{performance['Volatility']*100:.2f}%")
    st.metric("Max Drawdown", f"{performance['Max Drawdown']*100:.2f}%")

# ---------------- Disclaimer ----------------
st.caption(
    "⚠️ This tool is for educational and analytical purposes only. "
    "It does not constitute investment advice."
)
