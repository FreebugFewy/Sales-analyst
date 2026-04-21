from utils.deal_health import compute_deal_health


def test_strong_inputs_return_strong_band():
    score, band = compute_deal_health(win_rate=0.9, avg_days_to_close=30.0, mom_growth=0.1)
    assert band == "Strong"
    assert score >= 70


def test_weak_inputs_return_at_risk_band():
    score, band = compute_deal_health(win_rate=0.1, avg_days_to_close=180.0, mom_growth=-0.1)
    assert band == "At Risk"
    assert score < 40


def test_moderate_inputs_return_moderate_band():
    # win=0.4 → 18, growth=0 → 15, days=90 → 12.5  total=45.5
    score, band = compute_deal_health(win_rate=0.4, avg_days_to_close=90.0, mom_growth=0.0)
    assert band == "Moderate"
    assert 40 <= score < 70


def test_win_rate_dominates_weighting():
    import pytest
    # Hold growth and days equal; vary only win_rate
    score_high, _ = compute_deal_health(win_rate=0.9, avg_days_to_close=90.0, mom_growth=0.0)
    score_low, _ = compute_deal_health(win_rate=0.1, avg_days_to_close=90.0, mom_growth=0.0)
    # 0.9*45 - 0.1*45 = 36 pt difference; all other terms cancel
    assert score_high - score_low == pytest.approx(36.0, abs=0.1)


def test_score_clamped_to_100_on_perfect_inputs():
    score, _ = compute_deal_health(win_rate=1.0, avg_days_to_close=0.0, mom_growth=1.0)
    assert score == 100.0


def test_score_floored_at_zero_on_worst_inputs():
    score, _ = compute_deal_health(win_rate=0.0, avg_days_to_close=999.0, mom_growth=-1.0)
    assert score == 0.0


def test_score_of_70_is_strong_band():
    # win=1.0 (45), growth=-0.1 (gs=0, so 0), days=0 (ds=1.0, so 25): total=70
    score, band = compute_deal_health(win_rate=1.0, avg_days_to_close=0.0, mom_growth=-0.1)
    assert score == 70.0
    assert band == "Strong"


def test_score_of_40_is_moderate_band():
    # win=0.0 (0), growth=0.1 (gs=1.0, so 30), days=108 (ds=(1-108/180)=0.4, so 10): total=40
    score, band = compute_deal_health(win_rate=0.0, avg_days_to_close=108.0, mom_growth=0.1)
    assert score == 40.0
    assert band == "Moderate"
