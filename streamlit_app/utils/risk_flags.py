import pandas as pd


def compute_risk_flags(df: pd.DataFrame) -> list[dict]:
    flags = []

    for program in df["program"].unique():
        for region in df["region"].unique():
            subset = (
                df[(df["program"] == program) & (df["region"] == region)]
                .sort_values("month")
                .tail(3)
            )
            if len(subset) < 2:
                continue

            okr = subset["okr_attainment"].values
            adoption = subset["partner_adoption_rate"].values
            growth = subset["mom_growth"].values

            if (okr < 0.70).sum() >= 2:
                flags.append({
                    "program": program,
                    "region": region,
                    "flag_type": "OKR Miss",
                    "recommendation": (
                        f"{program} in {region} has missed its volume OKR in "
                        f"{int((okr < 0.70).sum())} of the last 3 months -- "
                        "recommend partner enablement review and OKR recalibration."
                    ),
                })

            if len(adoption) >= 2 and all(adoption[i] > adoption[i + 1] for i in range(len(adoption) - 1)):
                flags.append({
                    "program": program,
                    "region": region,
                    "flag_type": "Adoption Decline",
                    "recommendation": (
                        f"{program} in {region} shows consecutive month-over-month "
                        "decline in partner adoption rate -- recommend targeted outreach campaign."
                    ),
                })

            if (growth < 0).sum() >= 2:
                flags.append({
                    "program": program,
                    "region": region,
                    "flag_type": "Volume Decline",
                    "recommendation": (
                        f"{program} in {region} has experienced negative volume growth in "
                        f"{int((growth < 0).sum())} of the last 3 months -- recommend strategic review."
                    ),
                })

    return flags
