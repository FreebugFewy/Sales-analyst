from utils.health_score import compute_health_score


def test_all_max_inputs_returns_high():
    score, band = compute_health_score(okr_attainment=1.0, mom_growth=0.20, partner_adoption_rate=1.0)
    assert band == "High"
    assert score == 100.0


def test_all_zero_inputs_returns_low():
    # okr=0, growth=-0.20 (normalizes to 0), adoption=0 -> score=0
    score, band = compute_health_score(okr_attainment=0.0, mom_growth=-0.20, partner_adoption_rate=0.0)
    assert band == "Low"
    assert score == 0.0


def test_medium_band():
    # okr=0.7->28, growth=0->12.5, adoption=0.5->17.5 -> score=58
    score, band = compute_health_score(okr_attainment=0.70, mom_growth=0.0, partner_adoption_rate=0.50)
    assert band == "Medium"
    assert 40 <= score < 70


def test_high_band_boundary():
    # okr=1.0->40, growth=0.20->25, adoption=0.15->5.25 -> score=70.25 (High)
    score, band = compute_health_score(okr_attainment=1.0, mom_growth=0.20, partner_adoption_rate=0.15)
    assert band == "High"
    assert score >= 70.0


def test_okr_weight_dominates_adoption():
    score_high_okr, _ = compute_health_score(okr_attainment=1.0, mom_growth=0.0, partner_adoption_rate=0.0)
    score_high_adoption, _ = compute_health_score(okr_attainment=0.0, mom_growth=0.0, partner_adoption_rate=1.0)
    # OKR (40%) > adoption (35%)
    assert score_high_okr > score_high_adoption


def test_score_clamped_to_100():
    score, _ = compute_health_score(okr_attainment=1.0, mom_growth=0.20, partner_adoption_rate=1.0)
    assert score <= 100.0
