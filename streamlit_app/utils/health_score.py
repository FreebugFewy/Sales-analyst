def compute_health_score(
    okr_attainment: float,
    mom_growth: float,
    partner_adoption_rate: float,
) -> tuple[float, str]:
    growth_score = min(max((mom_growth + 0.20) / 0.40, 0.0), 1.0)
    score = okr_attainment * 40.0 + growth_score * 25.0 + partner_adoption_rate * 35.0
    score = round(min(score, 100.0), 1)
    band = "High" if score >= 70 else ("Medium" if score >= 40 else "Low")
    return score, band
