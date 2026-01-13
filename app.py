import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

from institutional_portfolio_analytics_project.portfolio.clients import clients
from institutional_portfolio_analytics_project.portfolio.optimizer import optimize_portfolio
from institutional_portfolio_analytics_project.analysis.performance import calculate_portfolio_performance


# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Institutional Portfolio Analytics", layout="centered")
st.title("📊 Institutional Portfolio Analytics Dashboard")


# ------------------- USER INPUTS -------------------
client_key = st.selectbox("Select Client Type", options=list(clients.keys()))
client = clients[client_key]

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

allocation_percentage = {k: v * 100 for k, v in weights.items()}
allocation_amount = {k: v * investment_amount for k, v in weights.items()}


# ------------------- ALLOCATION (%)
st.subheader("Recommended Portfolio Allocation (%)")

fig, ax = plt.subplots()
ax.bar(allocation_percentage.keys(), allocation_percentage.values())
ax.set_ylim(0, 100)

for i, v in enumerate(allocation_percentage.values()):
    ax.text(i, v + 1, f"{v:.1f}%", ha="center")

st.pyplot(fig)


# ------------------- ALLOCATION (₹)
st.subheader("Investment Allocation (₹)")

fig, ax = plt.subplots()
ax.bar(allocation_amount.keys(), allocation_amount.values())

for i, v in enumerate(allocation_amount.values()):
    ax.text(i, v, f"₹{v:,.0f}", ha="center", va="bottom")

st.pyplot(fig)


# ------------------- PERFORMANCE
st.subheader("Portfolio Performance Metrics")
st.write(performance)


# ============================================================
# 10-YEAR FUND GROWTH (FIXED & PROVEN DIFFERENT)
# ============================================================

st.subheader("10-Year Fund Growth Projections")

years = 10
years_array = np.arange(0, years + 1)

def grow(amount, rate):
    return amount * (1 + rate) ** years_array


# --- RETURN ASSUMPTIONS (DO NOT CHANGE)
db_min, db_max = 0.04, 0.06
dc_min, dc_max = 0.06, 0.09
end_min, end_max = 0.08, 0.12


# --- CALCULATIONS
db_min_v = grow(investment_amount, db_min)
db_max_v = grow(investment_amount, db_max)

dc_min_v = grow(investment_amount, dc_min)
dc_max_v = grow(investment_amount, dc_max)

end_min_v = grow(investment_amount, end_min)
end_max_v = grow(investment_amount, end_max)


# ------------------- DEBUG PROOF (REMOVE LATER)
st.subheader("DEBUG – Year-10 Values (Must Differ)")
st.write({
    "DB Min": round(db_min_v[-1], 2),
    "DB Max": round(db_max_v[-1], 2),
    "DC Min": round(dc_min_v[-1], 2),
    "DC Max": round(dc_max_v[-1], 2),
    "Endowment Min": round(end_min_v[-1], 2),
    "Endowment Max": round(end_max_v[-1], 2),
})


# ------------------- GRAPH 1: MAX RETURNS
st.subheader("Maximum Return Scenario (Optimistic)")

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(years_array, db_max_v, label="DB")
ax.plot(years_array, dc_max_v, label="DC")
ax.plot(years_array, end_max_v, label="Endowment")

ax.set_ylim(
    min(db_max_v.min(), dc_max_v.min(), end_max_v.min()) * 0.95,
    max(db_max_v.max(), dc_max_v.max(), end_max_v.max()) * 1.05
)

ax.set_xlabel("Years")
ax.set_ylabel("Portfolio Value (₹)")
ax.legend()
ax.grid(True)
st.pyplot(fig)


# ------------------- GRAPH 2: MIN RETURNS
st.subheader("Minimum Return Scenario (Conservative)")

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(years_array, db_min_v, label="DB")
ax.plot(years_array, dc_min_v, label="DC")
ax.plot(years_array, end_min_v, label="Endowment")

ax.set_ylim(
    min(db_min_v.min(), dc_min_v.min(), end_min_v.min()) * 0.95,
    max(db_min_v.max(), dc_min_v.max(), end_min_v.max()) * 1.05
)

ax.set_xlabel("Years")
ax.set_ylabel("Portfolio Value (₹)")
ax.legend()
ax.grid(True)
st.pyplot(fig)


# ------------------- FOOTER
st.caption("Educational use only. Not investment advice.")
