def compute_opportunity_score(
    annual_volume_m: float,
    avg_transaction_usd: float,
    interchange_rate: float,
    acceptance_rate: float,
    yoy_growth_rate: float,
) -> float:
    """
    Score a merchant's deal opportunity.

    Formula:
        gross_revenue          = annual_volume_m * avg_transaction_usd * interchange_rate
        growth_multiplier      = 1 + yoy_growth_rate
        network_gap_multiplier = 2.0 - acceptance_rate  (lower acceptance = more upside)

        score = gross_revenue * growth_multiplier * network_gap_multiplier

    Args:
        annual_volume_m: Annual transaction volume in millions
        avg_transaction_usd: Average transaction value in USD
        interchange_rate: Interchange rate as a decimal (e.g. 0.024 = 2.4%)
        acceptance_rate: Share of transactions approved as a decimal (e.g. 0.90). Expected range: [0, 1].
        yoy_growth_rate: Expected year-over-year volume growth as a decimal

    Returns:
        Raw opportunity score (higher = better deal candidate)
    """
    gross_revenue = annual_volume_m * avg_transaction_usd * interchange_rate
    growth_multiplier = 1 + yoy_growth_rate
    network_gap_multiplier = 2.0 - acceptance_rate
    return gross_revenue * growth_multiplier * network_gap_multiplier
