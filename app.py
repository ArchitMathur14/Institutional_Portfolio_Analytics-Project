import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

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
allocation_percentage = {k: v * 100 for k, v in weights.items()}
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


# ============================================================
# 10-YEAR FUND GROWTH SIMULATION (DB, DC, ENDOWMENT)
# ============================================================

st.subheader("10-Year Fund Growth Projections")

def simulate_fund_growth(initial_amount, min_return, max_return, years=10):
    timeline = np.arange(0, years + 1)
    min_growth = initial_amount * (1 + min_return) ** timeline
    max_growth = initial_amount * (1 + max_return) ** timeline

    return pd.DataFrame({
        "Year": timeline,
        "Min Growth": min_growth,
        "Max Growth": max_growth
    })


years = 10

# Assumptions
db_growth = simulate_fund_growth(investment_amount, 0.04, 0.06, years)
dc_growth = simulate_fund_growth(investment_amount, 0.06, 0.09, years)
endowment_growth = simulate_fund_growth(investment_amount, 0.08, 0.12, years)


# ------------------- GRAPH 1: MIN vs MAX SCENARIOS -------------------
fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(db_growth["Year"], db_growth["Min Growth"], "--", label="DB – Min")
ax.plot(db_growth["Year"], db_growth["Max Growth"], label="DB – Max")

ax.plot(dc_growth["Year"], dc_growth["Min Growth"], "--", label="DC – Min")
ax.plot(dc_growth["Year"], dc_growth["Max Growth"], label="DC – Max")

ax.plot(endowment_growth["Year"], endowment_growth["Min Growth"], "--", label="Endowment – Min")
ax.plot(endowment_growth["Year"], endowment_growth["Max Growth"], label="Endowment – Max")

ax.set_xlabel("Years")
ax.set_ylabel("Portfolio Value (₹)")
ax.set_title("10-Year Growth Projections: Min vs Max Scenarios")
ax.legend()
ax.grid(True)

st.pyplot(fig)


# ------------------- GRAPH 2: MAX RETURN COMPARISON -------------------
fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(db_gr_
