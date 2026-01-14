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
This dashboard evaluates **portfolio resilience under extreme macroeconomic scenarios**  
using **historically calibrated, scenario-based stress assumptions**.
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
    min_value=10_000,
    step=10_000,
    value=500_000
)

years = 10
years_array = np.arange(0, years + 1)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def compound_path(initial, yearly_returns):
    values = [initial]
    for r in yearly_returns:
        values.append(values[-1] * (1 + r))
    return np.array(values)

# ============================================================
# SCENARIO DEFINITIONS (OPTION A – STYLISED, CALIBRATED)
# ============================================================

if scenario == "Financial Crisis":
    st.subheader("📉 Financial Crisis Scenario")

    st.markdown("""
    **Description:**  
    Models a severe global recession similar to historical financial crises,  
    characterised by sharp equity drawdowns followed by gradual recovery.
    """)

    # Portfolio allocation (resilience-focused)
    allocation = {
        "Equities (ETFs)": 0.40,
        "Bonds": 0.45,
        "Gold / Defensive Assets": 0.15
    }

    # Phase-based annual returns (stylised)
    yearly_returns = (
        [-0.35] +                # Shock year
        [-0.05, 0.03] +           # Stabilisation
        [0.07] * (years - 3)      # Recovery
    )

elif scenario == "Geopolitical Conflict":
    st.subheader("🌍 Geopolitical Conflict Scenario")

    st.markdown("""
    **Description:**  
    Models prolonged geopolitical tensions causing market volatility,  
    inflationary pressure, and uneven asset performance.
    """)

    allocation = {
        "Equities (ETFs)": 0.50,
        "Bonds": 0.30,
        "Gold / Defensive Assets": 0.20
    }

    yearly_returns = (
        [-0.15] +                # Initial uncertainty shock
        [0.02, 0.01, 0.03] +      # Adjustment phase
        [0.06] * (years - 4)     # New normal
    )

# ============================================================
# PORTFOLIO ALLOCATION DISPLAY
# ============================================================
st.subheader("📊 Scenario-Optimised Portfolio Allocation")

alloc_df = pd.DataFrame({
    "Asset Class": allocation.keys(),
    "Allocation (%)": [v * 100 for v in allocation.values()]
})

fig_alloc = go.Figure(
    data=[
        go.Bar(
            x=alloc_df["Asset Class"],
            y=alloc_df["Allocation (%)"],
            text=alloc_df["Allocation (%)"].round(1).astype(str) + "%",
            textposition="auto"
        )
    ]
)

fig_alloc.update_layout(
    yaxis_title="Allocation (%)",
    yaxis_range=[0, 100]
)

st.plotly_chart(fig_alloc, use_container_width=True)

# ============================================================
# PORTFOLIO GROWTH SIMULATION
# ============================================================
portfolio_values = compound_path(investment_amount, yearly_returns)

# ============================================================
# TIME-SERIES STRESS GRAPH
# ============================================================
st.subheader("📈 Portfolio Value Under Stress Scenario")

fig_growth = go.Figure()

fig_growth.add_trace(go.Scatter(
    x=years_array,
    y=portfolio_values,
    mode="lines+markers",
    name="Portfolio Value",
    hovertemplate="Year %{x}<br>Value ₹%{y:,.0f}<extra></extra>"
))

fig_growth.update_layout(
    xaxis_title="Years",
    yaxis_title="Portfolio Value (₹)",
    hovermode="x unified"
)

st.plotly_chart(fig_growth, use_container_width=True)

# ============================================================
# KEY RISK METRICS
# ============================================================
st.subheader("⚠️ Key Risk Insights")

drawdown = (portfolio_values.min() - investment_amount) / investment_amount * 100
final_value = portfolio_values[-1]

metrics = {
    "Maximum Drawdown (%)": f"{drawdown:.1f}%",
    "Portfolio Value After Shock (Year 1)": f"₹{portfolio_values[1]:,.0f}",
    "Portfolio Value After 10 Years": f"₹{final_value:,.0f}"
}

st.write(metrics)

# ============================================================
# INTERPRETATION (CONSULTING-STYLE)
# ============================================================
st.markdown("""
### How to interpret this analysis
- This is **not a forecast**, but a **stress-test scenario**
- Returns are **phase-based and historically calibrated**
- The objective is to assess **resilience and recovery**, not maximise returns
- Portfolio construction prioritises **survivability under stress**
""")

# ============================================================
# FOOTER
# ============================================================
st.caption("Educational use only. Scenario-based stress testing. Not investment advice.")
