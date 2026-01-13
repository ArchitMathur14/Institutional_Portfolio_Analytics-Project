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

# Shared time axis (FIXES ALL ISSUES)
years = 10
years_array = np.arange(0, years + 1)

def simulate_fund_growth(initial_amount, annual_return, years_array):
    return initial_amount * (1 + annual_return) ** years_array


# ------------------- RETURN ASSUMPTIONS -------------------
db_min_return, db_max_return = 0.04, 0.06
dc_min_return, dc_max_return = 0.06, 0.09
end_min_return, end_max_return = 0.08, 0.12


# ------------------- GROWTH CALCULATIONS -------------------
db_min_values = simulate_fund_growth(investment_amount, db_min_return, years_array)
db_max_values = simulate_fund_growth(investment_amount, db_max_return, years_array)

dc_min_values = simulate_fund_growth(investment_amount, dc_min_return, years_array)
dc_max_values = simulate_fund_growth(investment_amount, dc_max_return, years_array)

end_min_values = simulate_fund_growth(investment_amount, end_min_return, years_array)
end_max_values = simulate_fund_growth(investment_amount, end_max_return, years_array)


# ------------------- GRAPH 1: MAX RETURN SCENARIO -------------------
st.subheader("10-Year Growth Projection – Maximum Return Scenario")

fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(years_array, db_max_values, label="DB Portfolio")
ax.plot(years_array, dc_max_values, label="DC Portfolio")
ax.plot(years_array, end_max_values, label="Endowment Portfolio")

ax.set_xlabel("Years")
ax.set_ylabel("Portfolio Value (₹)")
ax.set_title("Optimistic Scenario (Maximum Returns)")
ax.legend()
ax.grid(True)

st.pyplot(fig)


# ------------------- GRAPH 2: MIN RETURN SCENARIO -------------------
st.subheader("10-Year Growth Projection – Minimum Return Scenario")

fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(years_array, db_min_values, label="DB Portfolio")
ax.plot(years_array, dc_min_values, label="DC Portfolio")
ax.plot(years_array, end_min_values, label="Endowment Portfolio")

ax.set_xlabel("Years")
ax.set_ylabel("Portfolio Value (₹)")
ax.set_title("Conservative Scenario (Minimum Returns)")
ax.legend()
ax.grid(True)

st.pyplot(fig)


# ------------------- INSIGHTS -------------------
st.markdown("""
### Key Takeaways
- **DB portfolios** focus on capital preservation and predictable growth.
- **DC portfolios** balance risk and return for long-term wealth accumulation.
- **Endowment portfolios** maximise long-term compounding with higher volatility.
""")


# ------------------- FOOTER -------------------
st.caption("Educational use only. Not investment advice.")
