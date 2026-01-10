import pandas as pd
import numpy as np

def calculate_portfolio_performance(price_data, weights):
    weights = pd.Series(weights)
    returns = price_data.pct_change().dropna()
    portfolio_returns = returns.dot(weights)

    annual_return = portfolio_returns.mean() * 252
    volatility = portfolio_returns.std() * np.sqrt(252)
    sharpe_ratio = annual_return / volatility

    cumulative = (1 + portfolio_returns).cumprod()
    drawdown = cumulative / cumulative.cummax() - 1
    max_drawdown = drawdown.min()

    return {
        "Annual Return": annual_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown": max_drawdown
    }
