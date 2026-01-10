from pypfopt import expected_returns, risk_models, EfficientFrontier

def optimize_portfolio(price_data, target_allocation):
    mu = expected_returns.mean_historical_return(price_data)
    S = risk_models.sample_cov(price_data)

    ef = EfficientFrontier(mu, S, weight_bounds=(0.05, 0.70))
    ef.max_sharpe()

    weights = ef.clean_weights()
    performance = ef.portfolio_performance()

    return weights, performance
