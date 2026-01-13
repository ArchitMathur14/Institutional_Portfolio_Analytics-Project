import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

from institutional_portfolio_analytics_project.portfolio.clients import clients
from institutional_portfolio_analytics_project.portfolio.optimizer import optimize_portfolio
from institutional_portfolio_analytics_project.analysis.performance import calculate_portfolio_performance


# ------------------- PAGE CONFIG -------------------
st.set_page_config(
    page_title="Institutional Portfolio Analytics",
    layout="centered"
)

st.title("📊 Institutional Portfolio Analytics Dashboard")


# ------------------- USER INPUTS -------------------
client_key = st.selectbox(
    "Select Client Type",
    options=list(clients.keys())
)

client = clients[client_key]

st.subheader("Investment Amount")

investment_amount = st.number_input(
    "Enter total investment amount (₹)",
    min_value=1000,
    step=1000,
    value=100000
)


# ------------------- DATA LOADING -------------------
@st.cache_data
def load_market_data():
    tickers = ["SPY", "AGG", "VEA", "GLD"]
    data = yf.download(tickers, start="2019-01-01", auto_adjust=True)

    if isinstance(data.columns, pd.MultiIndex):
        data = data["Close"]

    return data.dropna()


prices = load_market_data()


# ------------------- PORTFOLIO OPTIMIZATION -------------------
weights, _ = optimize_portfolio(prices, client["target_allocation"])
performance = calculate_portfolio_performance(prices, weights)


# ------------------- ALLOCATION CALCULATIONS -------------------
# Convert weights (0–1) to %
allocation_percentage = {k: v * 100 for k, v in weights.items()}

# Convert weights to actual ₹ allocation
allocation_amount = {k: v * investment_amount for k, v in weights.items()}


# ------------------- % ALLOCATION CHART -------------------
st.subheader("Recommended Portfolio Allocation (%)")

fig, ax = plt.subplots()

ax.bar(allocation_percentage.keys(), allocation_percentage.values())
ax.set_ylabel("Allocation (%)")
ax.set_ylim(0, 100)

for i, v in enumerate(allocation_percentage.values()):
    ax.text(i, v + 1, f"{v:.1f}%", ha="center")

st.pyplot(fig)


# ------------------- ₹ ALLOCATION CHART -------------------
st.subheader("Investment Allocation (₹)")

fig, ax = plt.subplots()

ax.bar(allocation_amount.keys(), allocation_amount.values())
ax.set_ylabel("Amount Invested (₹)")

for i, v in enumerate(allocation_amount.values()):
    ax.text(i, v, f"₹{v:,.0f}", ha="center", va="bottom")

st.pyplot(fig)


# ------------------- ₹ ALLOCATION TEXT -------------------
st.subheader("Investment Breakdown")

for asset, amount in allocation_amount.items():
    st.write(f"**{asset}**: ₹{amount:,.0f}")


# ------------------- PERFORMANCE METRICS -------------------
st.subheader("Portfolio Performance Metrics")
st.write(performance)


# ------------------- FOOTER -------------------
st.caption("Educational use only. Not investment advice.")
st.subheader("Investment Strategy Overview")

st.markdown("""
**Growth Assets (Equities)**  
Focused on long-term capital appreciation through US and international equity exposure.

**Stability Assets (Bonds)**  
Designed to reduce volatility and provide steady returns through fixed-income investments.

**Diversification & Hedge (Gold)**  
Provides protection against inflation, market stress, and geopolitical uncertainty.
""")

