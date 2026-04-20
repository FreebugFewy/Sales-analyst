import pandas as pd
import numpy as np
from pathlib import Path

rng = np.random.default_rng(42)

PROGRAMS = [
    "USDC Settlement Rails",
    "Visa x Coinbase Card",
    "Visa x Crypto.com Card",
    "Crypto B2B Partnerships",
]
REGIONS = ["NA", "EU", "AP", "LAC", "MEA"]
REGION_WEIGHTS = {"NA": 0.40, "EU": 0.28, "AP": 0.20, "LAC": 0.07, "MEA": 0.05}

PROGRAM_CONFIG = {
    "USDC Settlement Rails": {
        "annual_volume_usd": 2_400_000_000,
        "avg_txn_usd": 50_000,
        "base_adoption_rate": 0.72,
        "monthly_trend": 0.012,
        "okr_stretch": 1.10,
        "max_partners": {"NA": 28, "EU": 20, "AP": 15, "LAC": 6, "MEA": 4},
    },
    "Visa x Coinbase Card": {
        "annual_volume_usd": 1_440_000_000,
        "avg_txn_usd": 450,
        "base_adoption_rate": 0.85,
        "monthly_trend": 0.018,
        "okr_stretch": 1.12,
        "max_partners": {"NA": 45, "EU": 32, "AP": 25, "LAC": 10, "MEA": 5},
    },
    "Visa x Crypto.com Card": {
        "annual_volume_usd": 1_080_000_000,
        "avg_txn_usd": 380,
        "base_adoption_rate": 0.78,
        "monthly_trend": 0.010,
        "okr_stretch": 1.15,
        "max_partners": {"NA": 35, "EU": 25, "AP": 30, "LAC": 8, "MEA": 6},
    },
    "Crypto B2B Partnerships": {
        "annual_volume_usd": 600_000_000,
        "avg_txn_usd": 12_000,
        "base_adoption_rate": 0.58,
        "monthly_trend": 0.022,
        "okr_stretch": 1.20,
        "max_partners": {"NA": 15, "EU": 12, "AP": 10, "LAC": 4, "MEA": 3},
    },
}


def generate():
    months = pd.date_range("2024-01-01", "2025-12-01", freq="MS")
    rows = []

    for program, config in PROGRAM_CONFIG.items():
        for region in REGIONS:
            weight = REGION_WEIGHTS[region]
            base_monthly_volume = config["annual_volume_usd"] * weight / 12
            base_adoption = config["base_adoption_rate"]
            max_partners = config["max_partners"][region]

            # Baked-in risk scenarios for Page 3 to surface
            mea_okr_miss = region == "MEA"
            lac_b2b_decline = program == "Crypto B2B Partnerships" and region == "LAC"

            prev_volume = base_monthly_volume
            prev_adoption = base_adoption

            for i, month in enumerate(months):
                trend_factor = 1 + config["monthly_trend"]
                noise = float(rng.normal(0, 0.03))

                # MEA: strong volume suppression in last 3 months to trigger OKR miss flag
                if mea_okr_miss and i >= 21:
                    noise -= 0.14

                volume = prev_volume * trend_factor * (1 + noise)
                volume = max(volume, base_monthly_volume * 0.1)

                okr_target = base_monthly_volume * (trend_factor ** i) * config["okr_stretch"]
                okr_attainment = float(np.clip(volume / okr_target, 0.30, 1.25))

                adoption_noise = float(rng.normal(0, 0.018))
                # LAC B2B: steady adoption decline in last 3 months
                if lac_b2b_decline and i >= 21:
                    adoption_noise -= 0.035
                adoption = float(np.clip(prev_adoption + adoption_noise, 0.20, 0.98))

                partners = max(1, int(max_partners * adoption * (0.85 + float(rng.random()) * 0.15)))
                txn_count = max(1, int(volume / config["avg_txn_usd"]))
                mom_growth = float((volume / prev_volume) - 1) if prev_volume > 0 else 0.0

                rows.append({
                    "month": month,
                    "program": program,
                    "region": region,
                    "volume_usd": round(volume, 2),
                    "transaction_count": txn_count,
                    "active_partners": partners,
                    "okr_attainment": round(okr_attainment, 4),
                    "mom_growth": round(mom_growth, 4),
                    "partner_adoption_rate": round(adoption, 4),
                })

                prev_volume = volume
                prev_adoption = adoption

    df = pd.DataFrame(rows)
    out_path = Path(__file__).parent / "data" / "crypto_programs.csv"
    out_path.parent.mkdir(exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} rows -> {out_path}")
    return df


if __name__ == "__main__":
    generate()
