from pypfopt import expected_returns, risk_models, EfficientFrontier


def optimize_portfolio(price_data, target_allocation):
    mu = expected_returns.mean_historical_return(price_data)
    S = risk_models.sample_cov(price_data)

    ef = EfficientFrontier(mu, S)

    assets = list(mu.index)

    # -----------------------------
    # INSTITUTIONAL CONSTRAINTS
    # -----------------------------
    MIN_WEIGHT = 0.05   # 5% minimum exposure to every asset
    MAX_WEIGHT = 0.70   # prevent over-concentration

    # Global min/max constraints
    ef.add_constraint(lambda w: w >= MIN_WEIGHT)
    ef.add_constraint(lambda w: w <= MAX_WEIGHT)

    # Target allocation soft-bounds
    for asset, target_weight in target_allocation.items():
        idx = assets.index(asset)

        lower_bound = max(MIN_WEIGHT, target_weight - 0.15)
        upper_bound = min(MAX_WEIGHT, target_weight + 0.15)

        ef.add_constraint(lambda w, i=idx, lb=lower_bound: w[i] >= lb)
        ef.add_constraint(lambda w, i=idx, ub=upper_bound: w[i] <= ub)

    # -----------------------------
    # OPTIMIZATION
    # -----------------------------
    ef.max_sharpe()

    weights = ef.clean_weights()
    performance = ef.portfolio_performance()

    return weights, performance
