from pypfopt import expected_returns, risk_models, EfficientFrontier

def optimize_portfolio(price_data, target_allocation):
    mu = expected_returns.mean_historical_return(price_data)
    S = risk_models.sample_cov(price_data)

    ef = EfficientFrontier(mu, S)

    # Add constraints so portfolio stays close to target allocation
    for asset, target_weight in target_allocation.items():
        ef.add_constraint(
            lambda w, asset=asset, tw=target_weight: w[list(mu.index).index(asset)] >= tw - 0.15
        )
        ef.add_constraint(
            lambda w, asset=asset, tw=target_weight: w[list(mu.index).index(asset)] <= tw + 0.15
        )

    ef.max_sharpe()
    weights = ef.clean_weights()
    performance = ef.portfolio_performance()

    return weights, performance
