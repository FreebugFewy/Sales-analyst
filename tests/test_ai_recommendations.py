import pandas as pd
from utils.ai_recommendations import compute_ai_recommendations


def _deal(deal_id, product, segment, acquirer_name, stage, days_in_stage, is_post_sale):
    return {
        "deal_id": deal_id,
        "product": product,
        "acquirer_segment": segment,
        "acquirer_name": acquirer_name,
        "deal_value_usd": 100_000.0,
        "stage": stage,
        "days_in_current_stage": days_in_stage,
        "total_days_in_flight": days_in_stage,
        "is_post_sale": is_post_sale,
        "days_to_first_revenue": None,
    }


def test_post_sale_over_14_days_is_critical():
    df = pd.DataFrame([_deal("VAS-0001", "Tap-to-Phone", "ISOs", "Paysafe", "Certification", 20, True)])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 1
    assert flags[0]["severity"] == "Critical"
    assert flags[0]["flag_type"] == "post_sale_stall"


def test_onboarding_between_10_and_14_days_is_warning():
    df = pd.DataFrame([_deal("VAS-0002", "Tokenization Suite", "Fintechs", "Stripe", "Onboarding", 12, True)])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 1
    assert flags[0]["severity"] == "Warning"
    assert flags[0]["flag_type"] == "onboarding_cert_delay"


def test_pre_sale_over_21_days_is_warning():
    df = pd.DataFrame([_deal("VAS-0003", "Acceptance API", "Regional Banks", "First National Bank", "Proposal", 25, False)])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 1
    assert flags[0]["severity"] == "Warning"
    assert flags[0]["flag_type"] == "pre_sale_stall"


def test_pre_sale_between_14_and_21_days_is_watch():
    df = pd.DataFrame([_deal("VAS-0004", "Visa Acceptance Console", "Tier 1 Banks", "JPMorgan Chase", "Negotiation", 17, False)])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 1
    assert flags[0]["severity"] == "Watch"
    assert flags[0]["flag_type"] == "pre_sale_approaching"


def test_healthy_deal_produces_no_flags():
    df = pd.DataFrame([_deal("VAS-0005", "Tap-to-Phone", "ISOs", "Cayan", "Onboarding", 5, True)])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 0


def test_next_best_action_non_empty_for_every_flag():
    df = pd.DataFrame([
        _deal("VAS-0006", "Tap-to-Phone", "ISOs", "Paysafe", "Certification", 20, True),
        _deal("VAS-0007", "Acceptance API", "Fintechs", "Adyen", "Proposal", 30, False),
    ])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 2
    assert all(len(f["next_best_action"]) > 0 for f in flags)


def test_onboarding_over_14_days_escalates_to_critical():
    df = pd.DataFrame([_deal("VAS-0008", "Tap-to-Phone", "ISOs", "Paysafe", "Onboarding", 15, True)])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 1
    assert flags[0]["severity"] == "Critical"
    assert flags[0]["flag_type"] == "post_sale_stall"
