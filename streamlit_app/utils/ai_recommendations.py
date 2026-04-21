import pandas as pd

_POST_SALE_STALL = 14
_ONBOARDING_CERT_WATCH = 10
_PRE_SALE_STALL = 21
_PRE_SALE_WATCH = 14


def compute_ai_recommendations(deals_df: pd.DataFrame) -> list[dict]:
    """
    Compute AI-driven deal flags and recommendations based on stage duration.

    Args:
        deals_df: DataFrame with deal records containing: deal_id, product, acquirer_segment,
                 acquirer_name, stage, days_in_current_stage, is_post_sale

    Returns:
        List of flag dictionaries with fields: deal_id, product, acquirer_segment, stage,
        severity, flag_type, next_best_action
    """
    flags = []
    for _, row in deals_df.iterrows():
        days = int(row["days_in_current_stage"])
        stage = str(row["stage"])
        flag_fields: dict | None = None

        if row["is_post_sale"]:
            if days > _POST_SALE_STALL:
                flag_fields = {
                    "severity": "Critical",
                    "flag_type": "post_sale_stall",
                    "next_best_action": (
                        f"{row['product']} deal with {row['acquirer_name']} stalled in "
                        f"{stage} for {days} days — schedule escalation call with "
                        f"{row['acquirer_segment']} integration team to unblock."
                    ),
                }
            elif stage in ("Onboarding", "Certification") and days > _ONBOARDING_CERT_WATCH:
                flag_fields = {
                    "severity": "Warning",
                    "flag_type": "onboarding_cert_delay",
                    "next_best_action": (
                        f"{row['product']} deal with {row['acquirer_name']} has been in "
                        f"{stage} for {days} days — verify technical readiness checklist completion."
                    ),
                }
        else:
            if days > _PRE_SALE_STALL:
                flag_fields = {
                    "severity": "Warning",
                    "flag_type": "pre_sale_stall",
                    "next_best_action": (
                        f"{row['product']} deal with {row['acquirer_name']} stalled in "
                        f"{stage} for {days} days — review deal blockers and schedule follow-up."
                    ),
                }
            elif days > _PRE_SALE_WATCH:
                flag_fields = {
                    "severity": "Watch",
                    "flag_type": "pre_sale_approaching",
                    "next_best_action": (
                        f"{row['product']} deal with {row['acquirer_name']} approaching stall "
                        f"threshold in {stage} ({days} days) — proactively check in with stakeholder."
                    ),
                }

        if flag_fields:
            flags.append({
                "deal_id": row["deal_id"],
                "product": row["product"],
                "acquirer_segment": row["acquirer_segment"],
                "stage": stage,
                **flag_fields,
            })
    return flags
