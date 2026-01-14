import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from institutional_portfolio_analytics_project.portfolio.clients import clients
from institutional_portfolio_analytics_project.portfolio.optimizer import optimize_portfolio
from institutional_portfolio_analytics_project.analysis.performance import calculate_portfolio_performance


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Institutional Portfolio Analytics", layout="centered")
st.title("📊 Institutional Portfolio Analytics Dashboard")


# ============================================================
# USER INPUTS
# ============================================================
client_key = st.selectbox("Select Client Type", options=list(clients.keys()))
client = clients[client_key]

investment_amount = st.number_input(
    "Enter total investment amount (₹)",
    min_value=1000,
    step=1000,
    value=100000
)

inflation_rate = st.slider(
    "Assumed Inflation Rate (%)",
    min_value=2.0,
    max_value=8.0,
    value=5.0
) / 100


# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_market_data():
    tickers = ["SPY", "AGG", "VEA", "GLD"]
    data = yf.download(tickers, start="2019-01-01", auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data = data["Close"]
    return data.dropna()

prices = load_market_data()


# ============================================================
# PORTFOLIO OPTIMIZATION
# ============================================================
weights, _ = optimize_portfolio(prices, client["target_allocation"])
performance = calculate_portfolio_performance(prices, weights)

allocation_percentage = {k: v * 100 for k, v in weights.items()}
allocation_amount = {k: v * investment_amount for k, v in weights.items()}


# ============================================================
# ALLOCATION CHARTS
# ============================================================
st.subheader("Recommended Portfolio Allocation (%)")
fig, ax = plt.subplots()
ax.bar(allocation_percentage.keys(), allocation_percentage.values())
ax.set_ylim(0, 100)
for i, v in enumerate(allocation_percentage.values()):
    ax.text(i, v + 1, f"{v:.1f}%", ha="center")
st.pyplot(fig)

st.subheader("Investment Allocation (₹)")
fig, ax = plt.subplots()
ax.bar(allocation_amount.keys(), allocation_amount.values())
for i, v in enumerate(allocation_amount.values()):
    ax.text(i, v, f"₹{v:,.0f}", ha="center", va="bottom")
st.pyplot(fig)

st.subheader("Portfolio Performance Metrics")
st.write(performance)


# ============================================================
# GROWTH + INFLATION LOGIC
# ============================================================
years = 10
years_array = np.arange(0, years + 1)

def grow(amount, rate):
    return amount * (1 + rate) ** years_array

def real_return(nominal, inflation):
    return (1 + nominal) / (1 + inflation) - 1


# ============================================================
# CLIENT-SPECIFIC ASSUMPTIONS
# ============================================================
client_returns = {
    "DB": (0.04, 0.06),
    "DC": (0.06, 0.09),
    "Endowment": (0.08, 0.12)
}

nominal_min, nominal_max = client_returns[client_key]

# Convert to REAL returns (this is the fix)
real_min = real_return(nominal_min, inflation_rate)
real_max = real_return(nominal_max, inflation_rate)

min_growth = grow(investment_amount, real_min)
max_growth = grow(investment_amount, real_max)


# ============================================================
# MAX RETURN GRAPH (CLIENT ONLY, REAL RETURNS)
# ============================================================
st.subheader(f"{client_key} Portfolio – Maximum Return Scenario (Real)")

fig_max = go.Figure()

fig_max.add_trace(go.Scatter(
    x=years_array,
    y=max_growth,
    mode="lines+markers",
    name=f"{client_key} Max",
    hovertemplate="Year %{x}<br>Value ₹%{y:,.0f}<extra></extra>"
))

fig_max.update_layout(
    xaxis_title="Years",
    yaxis_title="Portfolio Value (₹, Inflation-Adjusted)",
    hovermode="x unified"
)

st.plotly_chart(fig_max, use_container_width=True)


# ============================================================
# MIN RETURN GRAPH (CLIENT ONLY, REAL RETURNS)
# ============================================================
st.subheader(f"{client_key} Portfolio – Minimum Return Scenario (Real)")

fig_min = go.Figure()

fig_min.add_trace(go.Scatter(
    x=years_array,
    y=min_growth,
    mode="lines+markers",
    name=f"{client_key} Min",
    hovertemplate="Year %{x}<br>Value ₹%{y:,.0f}<extra></extra>"
))

fig_min.update_layout(
    xaxis_title="Years",
    yaxis_title="Portfolio Value (₹, Inflation-Adjusted)",
    hovermode="x unified"
)

st.plotly_chart(fig_min, use_container_width=True)


# ============================================================
# CLEAR EXPLANATION (VERY IMPORTANT)
# ============================================================
st.markdown(f"""
### How to interpret this
- The graphs show **inflation-adjusted (real) portfolio growth**
- Inflation assumption: **{inflation_rate*100:.1f}%**
- Only the selected **{client_key} portfolio** is shown
- Values represent **purchasing power**, not nominal rupees
""")


# ============================================================
# FOOTER
# ============================================================
st.caption("Educational use only. Not investment advice.")
