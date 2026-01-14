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
# GROWTH ASSUMPTIONS
# ============================================================
years = 10
years_array = np.arange(0, years + 1)

def grow(amount, rate):
    return amount * (1 + rate) ** years_array

def real_return(nominal, inflation):
    return (1 + nominal) / (1 + inflation) - 1


# Nominal return assumptions
db_min, db_max = 0.04, 0.06
dc_min, dc_max = 0.06, 0.09
end_min, end_max = 0.08, 0.12


# ============================================================
# NOMINAL GROWTH
# ============================================================
db_max_v = grow(investment_amount, db_max)
dc_max_v = grow(investment_amount, dc_max)
end_max_v = grow(investment_amount, end_max)

db_min_v = grow(investment_amount, db_min)
dc_min_v = grow(investment_amount, dc_min)
end_min_v = grow(investment_amount, end_min)


# ============================================================
# INTERACTIVE GROWTH CHARTS
# ============================================================
st.subheader("Maximum Return Scenario (Optimistic)")

fig_max = go.Figure()
fig_max.add_trace(go.Scatter(x=years_array, y=db_max_v, name="DB",
                             hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>"))
fig_max.add_trace(go.Scatter(x=years_array, y=dc_max_v, name="DC",
                             hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>"))
fig_max.add_trace(go.Scatter(x=years_array, y=end_max_v, name="Endowment",
                             hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>"))
fig_max.update_layout(xaxis_title="Years", yaxis_title="Portfolio Value (₹)", hovermode="x unified")
st.plotly_chart(fig_max, use_container_width=True)

st.subheader("Minimum Return Scenario (Conservative)")

fig_min = go.Figure()
fig_min.add_trace(go.Scatter(x=years_array, y=db_min_v, name="DB",
                             hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>"))
fig_min.add_trace(go.Scatter(x=years_array, y=dc_min_v, name="DC",
                             hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>"))
fig_min.add_trace(go.Scatter(x=years_array, y=end_min_v, name="Endowment",
                             hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>"))
fig_min.update_layout(xaxis_title="Years", yaxis_title="Portfolio Value (₹)", hovermode="x unified")
st.plotly_chart(fig_min, use_container_width=True)


# ============================================================
# INFLATION-ADJUSTED RETURNS (ENDOWMENT DEMO)
# ============================================================
st.subheader("Nominal vs Inflation-Adjusted Growth (Endowment)")

end_real_rate = real_return(0.10, inflation_rate)
end_real_growth = grow(investment_amount, end_real_rate)

fig_real = go.Figure()
fig_real.add_trace(go.Scatter(x=years_array, y=end_max_v, name="Nominal Growth",
                              hovertemplate="₹%{y:,.0f}<extra></extra>"))
fig_real.add_trace(go.Scatter(x=years_array, y=end_real_growth, name="Real Growth",
                              hovertemplate="₹%{y:,.0f}<extra></extra>"))

fig_real.update_layout(xaxis_title="Years", yaxis_title="Portfolio Value (₹)", hovermode="x unified")
st.plotly_chart(fig_real, use_container_width=True)


# ============================================================
# MONTE CARLO SIMULATION (ENDOWMENT)
# ============================================================
st.subheader("Monte Carlo Simulation – Endowment Portfolio")

def monte_carlo(initial, mean, vol, years, sims=5000):
    returns = np.random.normal(mean, vol, (years, sims))
    paths = np.zeros((years + 1, sims))
    paths[0] = initial
    for t in range(1, years + 1):
        paths[t] = paths[t - 1] * (1 + returns[t - 1])
    return paths

end_mc = monte_carlo(investment_amount, 0.10, 0.18, years)

fig_mc = go.Figure()
for i in range(200):
    fig_mc.add_trace(go.Scatter(
        x=years_array,
        y=end_mc[:, i],
        line=dict(color="lightgrey"),
        showlegend=False,
        hoverinfo="skip"
    ))

fig_mc.add_trace(go.Scatter(
    x=years_array,
    y=np.percentile(end_mc, 50, axis=1),
    line=dict(color="blue", width=3),
    name="Median Outcome"
))

fig_mc.update_layout(xaxis_title="Years", yaxis_title="Portfolio Value (₹)", hovermode="x unified")
st.plotly_chart(fig_mc, use_container_width=True)

st.markdown("### Monte Carlo Outcomes (Year 10)")
st.write({
    "Worst 5% Outcome": f"₹{np.percentile(end_mc[-1], 5):,.0f}",
    "Median Outcome": f"₹{np.percentile(end_mc[-1], 50):,.0f}",
    "Best 5% Outcome": f"₹{np.percentile(end_mc[-1], 95):,.0f}",
})


# ============================================================
# FOOTER
# ============================================================
st.caption("Educational use only. Not investment advice.")
