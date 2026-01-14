import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Scenario-Based Portfolio Stress Testing",
    layout="centered"
)

st.title("📉 Scenario-Based Portfolio Stress Testing Dashboard")

st.markdown("""
This tool demonstrates **scenario-based portfolio stress testing and tactical rebalancing**  
using **historically informed, rule-based assumptions**.
""")

# ============================================================
# USER INPUTS
# ============================================================
scenario = st.selectbox(
    "Select Stress Scenario",
    options=[
        "Financial Crisis",
        "Geopolitical Conflict"
    ]
)

investment_amount = st.number_input(
    "Investment Amount (₹)",
    min_value=100_000,
    step=100_000,
    value=1_000_000
)

years = 10
years_array = np.arange(0, years + 1)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def compound_path(initial, returns):
    values = [initial]
    for r in returns:
        values.append(values[-1] * (1 + r))
    return np.array(values)

def tactical_signal(price_path):
    peak = price_path[0]
    signals = []

    for year, price in enumerate(price_path):
        drawdown = (price - peak) / peak

        if drawdown <= -0.25:
            signals.append("BUY (Deep Value Zone)")
        elif price >= peak * 1.10:
            signals.append("SELL (Profit Taking)")
        else:
            signals.append("HOLD")

    return signals

# ============================================================
# SCENARIO DEFINITIONS
# ============================================================

if scenario == "Financial Crisis":
    st.subheader("📉 Financial Crisis Scenario")

    assets = {
        "S&P 500 ETF (Equity)": 0.40,
        "US Aggregate Bond ETF": 0.45,
        "Gold ETF": 0.15
    }

    yearly_returns = (
        [-0.35] +
        [-0.05, 0.03] +
        [0.07] * (years - 3)
    )

elif scenario == "Geopolitical Conflict":
    st.subheader("🌍 Geopolitical Conflict Scenario")

    assets = {
        "S&P 500 ETF (Equity)": 0.50,
        "US Aggregate Bond ETF": 0.30,
        "Gold ETF": 0.20
    }

    yearly_returns = (
        [-0.15] +
        [0.02, 0.01, 0.03] +
        [0.06] * (years - 4)
    )

# ============================================================
# ALLOCATION DISPLAY
# ============================================================
st.subheader("📊 Recommended Portfolio Allocation")

alloc_df = pd.DataFrame({
    "Asset": assets.keys(),
    "Allocation (%)": [v * 100 for v in assets.values()],
    "Amount Invested (₹)": [v * investment_amount for v in assets.values()]
})

st.dataframe(alloc_df, use_container_width=True)

# ============================================================
# PORTFOLIO SIMULATION
# ============================================================
portfolio_values = compound_path(investment_amount, yearly_returns)
signals = tactical_signal(portfolio_values)

# ============================================================
# PORTFOLIO VALUE GRAPH
# ============================================================
st.subheader("📈 Portfolio Value Under Scenario")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=years_array,
    y=portfolio_values,
    mode="lines+markers",
    name="Portfolio Value",
    hovertemplate="Year %{x}<br>Value ₹%{y:,.0f}<extra></extra>"
))

fig.update_layout(
    xaxis_title="Years",
    yaxis_title="Portfolio Value (₹)",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# BUY / SELL SIGNALS
# ============================================================
st.subheader("🛠 Tactical Buy / Sell Guidance")

signal_df = pd.DataFrame({
    "Year": years_array,
    "Portfolio Value (₹)": portfolio_values.round(0),
    "Suggested Action": signals
})

st.dataframe(signal_df, use_container_width=True)

# ============================================================
# EXPLANATION (CRITICAL)
# ============================================================
st.markdown("""
### How the buy / sell logic works
- **BUY** signals trigger when the portfolio falls **25% or more from peak**
- **SELL** signals trigger after recovery beyond **pre-shock levels**
- This represents **rule-based rebalancing**, not market timing
- The objective is to **improve recovery outcomes**, not predict bottoms
""")

# ============================================================
# RISK INSIGHTS
# ============================================================
drawdown = (portfolio_values.min() - investment_amount) / investment_amount * 100

st.markdown("### Key Risk Insights")
st.write({
    "Maximum Drawdown (%)": f"{drawdown:.1f}%",
    "Lowest Portfolio Value": f"₹{portfolio_values.min():,.0f}",
    "Portfolio Value After 10 Years": f"₹{portfolio_values[-1]:,.0f}"
})

# ============================================================
# FOOTER
# ============================================================
st.caption(
    "Educational use only. Scenario-based stress testing and rule-based rebalancing. "
    "Not investment advice."
)
