import pandas as pd
from utils.risk_flags import compute_risk_flags


def _make_df(okr_values, adoption_values, growth_values, program="Test Program", region="NA"):
    months = pd.date_range("2025-10-01", periods=len(okr_values), freq="MS")
    return pd.DataFrame({
        "month": months,
        "program": program,
        "region": region,
        "okr_attainment": okr_values,
        "partner_adoption_rate": adoption_values,
        "mom_growth": growth_values,
        "volume_usd": [1e9] * len(okr_values),
        "transaction_count": [100_000] * len(okr_values),
        "active_partners": [20] * len(okr_values),
    })


def test_okr_miss_flag_raised():
    df = _make_df([0.55, 0.60, 0.58], [0.80, 0.80, 0.80], [0.05, 0.05, 0.05])
    flags = compute_risk_flags(df)
    assert any(f["flag_type"] == "OKR Miss" for f in flags)


def test_healthy_program_raises_no_flags():
    df = _make_df([0.92, 0.88, 0.95], [0.80, 0.82, 0.81], [0.04, 0.06, 0.05])
    flags = compute_risk_flags(df)
    assert flags == []


def test_adoption_decline_flag_raised():
    df = _make_df([0.90, 0.90, 0.90], [0.80, 0.72, 0.64], [0.05, 0.05, 0.05])
    flags = compute_risk_flags(df)
    assert any(f["flag_type"] == "Adoption Decline" for f in flags)


def test_volume_decline_flag_raised():
    df = _make_df([0.90, 0.90, 0.90], [0.80, 0.80, 0.80], [-0.04, -0.06, -0.03])
    flags = compute_risk_flags(df)
    assert any(f["flag_type"] == "Volume Decline" for f in flags)


def test_recommendation_non_empty_for_all_flags():
    df = _make_df([0.55, 0.60, 0.58], [0.80, 0.80, 0.80], [0.05, 0.05, 0.05])
    flags = compute_risk_flags(df)
    assert len(flags) > 0
    for flag in flags:
        assert isinstance(flag["recommendation"], str)
        assert len(flag["recommendation"]) > 0
