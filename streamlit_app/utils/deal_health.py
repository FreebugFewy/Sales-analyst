def compute_deal_health(
    win_rate: float,
    avg_days_to_close: float,
    mom_growth: float,
) -> tuple[float, str]:
    """
    Compute deal health score and band.

    Args:
        win_rate: Win rate as a float between 0 and 1
        avg_days_to_close: Average days to close deals
        mom_growth: Month-over-month growth rate

    Returns:
        Tuple of (score, band) where score is 0-100 and band is "Strong", "Moderate", or "At Risk"
    """
    days_score = max(0.0, 1.0 - avg_days_to_close / 180.0)
    growth_score = min(1.0, max(0.0, (mom_growth + 0.1) / 0.2))
    score = win_rate * 45.0 + growth_score * 30.0 + days_score * 25.0
    score = round(min(100.0, max(0.0, score)), 1)
    band = "Strong" if score >= 70 else ("Moderate" if score >= 40 else "At Risk")
    return score, band
