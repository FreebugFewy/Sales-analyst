import pandas as pd
import streamlit as st

from utils.ai_recommendations import compute_ai_recommendations
from utils.data_loader import load_deals

st.set_page_config(page_title="AI Insight Engine", page_icon="🤖", layout="wide")

df = load_deals()
flags = compute_ai_recommendations(df)

_SEVERITY_ORDER = {"Critical": 0, "Warning": 1, "Watch": 2}
_SEVERITY_COLORS = {"Critical": "#f8d7da", "Warning": "#fff3cd", "Watch": "#d1ecf1"}

if flags:
    flags_df = pd.DataFrame(flags)
    flags_df["_order"] = flags_df["severity"].map(_SEVERITY_ORDER)
    flags_df = flags_df.sort_values("_order").drop(columns="_order").reset_index(drop=True)
else:
    flags_df = pd.DataFrame(
        columns=["deal_id", "product", "acquirer_segment", "stage", "severity", "next_best_action"]
    )

critical_count = int((flags_df["severity"] == "Critical").sum()) if len(flags_df) else 0
warning_count = int((flags_df["severity"] == "Warning").sum()) if len(flags_df) else 0
watch_count = int((flags_df["severity"] == "Watch").sum()) if len(flags_df) else 0

st.title("AI Insight Engine")
st.caption("Automated deal monitoring and next-best-action recommendations · NA VAS")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Flags", len(flags_df))
col2.metric("Critical", critical_count)
col3.metric("Warning", warning_count)
col4.metric("Watch", watch_count)

st.divider()
st.subheader("Deal Recommendations")

if len(flags_df) == 0:
    st.success("No flags — all deals are progressing on track.")
else:
    display_df = flags_df[
        ["deal_id", "product", "acquirer_segment", "stage", "severity", "next_best_action"]
    ].rename(
        columns={
            "deal_id": "Deal ID",
            "product": "Product",
            "acquirer_segment": "Segment",
            "stage": "Stage",
            "severity": "Severity",
            "next_best_action": "Next Best Action",
        }
    )

    def _color_severity(val: str) -> str:
        return f"background-color: {_SEVERITY_COLORS.get(val, '')}"

    st.dataframe(
        display_df.style.map(_color_severity, subset=["Severity"]),
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.subheader("Strategic Priorities")
st.markdown("""
**Q2 2026 Priorities — NA VAS Sales Enablement**

1. **Resolve Certification bottleneck (est. 5–8 days revenue delay per deal):** \
Certification is the longest post-sale stage across all products. \
Recommend deploying a structured technical readiness checklist at Intake to surface \
integration gaps earlier, reducing Certification cycle time by an estimated 30%.

2. **Arrest ISO win-rate decline:** ISOs close fastest but win rate has trended down \
two consecutive quarters. Recommend targeted seller enablement — competitive \
battle cards and a streamlined Proposal-to-close playbook specific to the ISO segment \
to recover 5–8 percentage points.

3. **Accelerate Tap-to-Phone onboarding in Regional Bank segment:** Regional Banks show \
the highest post-sale stall rate for Tap-to-Phone. Recommend a dedicated onboarding \
concierge for the first 90 days post-close, reducing time-to-first-revenue by \
an estimated 20 days.
""")
