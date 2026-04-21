import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

PRODUCTS = [
    "Tap-to-Phone",
    "Tokenization Suite",
    "Acceptance API",
    "Visa Acceptance Console",
]
SEGMENTS = ["Tier 1 Banks", "Regional Banks", "ISOs", "Fintechs"]
PRE_SALE_STAGES = ["Prospecting", "Qualification", "Proposal", "Negotiation"]
POST_SALE_STAGES = ["Intake", "Onboarding", "Certification", "Activation", "Live"]

ACQUIRER_NAMES = {
    "Tier 1 Banks": ["JPMorgan Chase", "Bank of America", "Wells Fargo", "Citibank", "US Bancorp"],
    "Regional Banks": ["First National Bank", "Pacific Premier", "Glacier Bancorp", "Heartland Financial", "Renasant Bank"],
    "ISOs": ["Priority Payment Systems", "Paysafe", "EVO Payments", "Cayan", "Shift4"],
    "Fintechs": ["Stripe", "Square", "Adyen", "Marqeta", "Checkout.com"],
}

BASE_WIN_RATE = {"Tier 1 Banks": 0.35, "Regional Banks": 0.42, "ISOs": 0.55, "Fintechs": 0.48}
BASE_DEAL_SIZE = {"Tier 1 Banks": 850_000, "Regional Banks": 420_000, "ISOs": 95_000, "Fintechs": 210_000}
BASE_DAYS_TO_CLOSE = {"Tier 1 Banks": 120, "Regional Banks": 90, "ISOs": 45, "Fintechs": 75}
PRODUCT_MODIFIER = {"Tap-to-Phone": 1.0, "Tokenization Suite": 1.2, "Acceptance API": 0.9, "Visa Acceptance Console": 1.1}
POST_SALE_STAGE_THRESHOLD = {"Intake": 5, "Onboarding": 10, "Certification": 14, "Activation": 7, "Live": 999}


def _generate_pipeline_monthly() -> pd.DataFrame:
    months = pd.date_range("2025-01", periods=18, freq="MS")
    rows = []
    for i, month in enumerate(months):
        for product in PRODUCTS:
            for segment in SEGMENTS:
                mod = PRODUCT_MODIFIER[product]
                trend = 1 + 0.01 * i
                noise = np.random.normal(1, 0.05)

                deals_created = max(1, int(np.random.poisson(8) * mod))
                win_rate = float(np.clip(
                    BASE_WIN_RATE[segment] * noise + 0.004 * i * np.random.choice([-1, 1]),
                    0.1, 0.9,
                ))
                deals_won = int(deals_created * win_rate)
                avg_deal_size = BASE_DEAL_SIZE[segment] * mod * noise * trend
                pipeline_value = deals_created * avg_deal_size * (1 - win_rate)
                avg_days = float(np.clip(BASE_DAYS_TO_CLOSE[segment] * np.random.normal(1, 0.1), 10, 300))
                prev_pipeline = pipeline_value * np.random.normal(0.97, 0.03)
                mom_growth = (pipeline_value - prev_pipeline) / prev_pipeline if prev_pipeline > 0 else 0.0

                rows.append({
                    "month": month,
                    "product": product,
                    "acquirer_segment": segment,
                    "deals_created": deals_created,
                    "deals_won": deals_won,
                    "pipeline_value_usd": round(pipeline_value, 2),
                    "avg_deal_size_usd": round(avg_deal_size, 2),
                    "win_rate": round(win_rate, 4),
                    "avg_days_to_close": round(avg_days, 1),
                    "mom_growth": round(mom_growth, 4),
                })
    return pd.DataFrame(rows)


def _generate_deals(n: int = 200) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        product = np.random.choice(PRODUCTS)
        segment = np.random.choice(SEGMENTS)
        acquirer_name = np.random.choice(ACQUIRER_NAMES[segment])
        is_post_sale = np.random.random() < 0.4

        if is_post_sale:
            stage = str(np.random.choice(
                POST_SALE_STAGES, p=[0.10, 0.25, 0.35, 0.20, 0.10]
            ))
            threshold = POST_SALE_STAGE_THRESHOLD[stage]
            if np.random.random() < 0.35:
                days_in_stage = int(np.random.uniform(threshold + 1, threshold * 2.5))
            else:
                days_in_stage = int(np.random.uniform(1, threshold))
        else:
            stage = str(np.random.choice(PRE_SALE_STAGES))
            if np.random.random() < 0.30:
                days_in_stage = int(np.random.uniform(22, 45))
            else:
                days_in_stage = int(np.random.uniform(1, 21))

        total_days = int(np.random.uniform(days_in_stage, days_in_stage * 2))
        deal_value = max(10_000.0, BASE_DEAL_SIZE[segment] * float(np.random.normal(1, 0.2)))
        days_to_first_revenue = int(np.random.uniform(30, 120)) if stage == "Live" else None

        rows.append({
            "deal_id": f"VAS-{i:04d}",
            "product": product,
            "acquirer_segment": segment,
            "acquirer_name": acquirer_name,
            "deal_value_usd": round(deal_value, 2),
            "stage": stage,
            "days_in_current_stage": days_in_stage,
            "total_days_in_flight": total_days,
            "is_post_sale": is_post_sale,
            "days_to_first_revenue": days_to_first_revenue,
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = Path(__file__).parent / "data"
    out.mkdir(exist_ok=True)

    pipeline_df = _generate_pipeline_monthly()
    pipeline_df.to_csv(out / "pipeline_monthly.csv", index=False)
    print(f"pipeline_monthly.csv: {len(pipeline_df)} rows")

    deals_df = _generate_deals()
    deals_df.to_csv(out / "deals.csv", index=False)
    print(f"deals.csv: {len(deals_df)} rows")
