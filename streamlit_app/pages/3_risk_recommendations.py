import streamlit as st
import pandas as pd
from utils.data_loader import load_data
from utils.risk_flags import compute_risk_flags

st.set_page_config(page_title="Risk & Recommendations", page_icon="⚠️", layout="wide")

df = load_data()
flags = compute_risk_flags(df)
flags_df = pd.DataFrame(flags) if flags else pd.DataFrame(
    columns=["program", "region", "flag_type", "recommendation"]
)

st.title("Risk & Recommendations")
st.caption("Automated flag engine -- surfaces threshold breaches before they reach exec escalation.")

st.divider()

n_okr = len(flags_df[flags_df["flag_type"] == "OKR Miss"]) if len(flags_df) else 0
n_adoption = len(flags_df[flags_df["flag_type"] == "Adoption Decline"]) if len(flags_df) else 0
n_volume = len(flags_df[flags_df["flag_type"] == "Volume Decline"]) if len(flags_df) else 0
total_flags = len(flags_df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Flags", total_flags)
col2.metric("OKR Misses", n_okr)
col3.metric("Adoption Declines", n_adoption)
col4.metric("Volume Declines", n_volume)

st.divider()
st.subheader("Active Risk Flags")

if len(flags_df) == 0:
    st.success("No active risk flags. All programs are within healthy thresholds.")
else:
    FLAG_ICONS = {
        "OKR Miss": "🔴",
        "Adoption Decline": "🟡",
        "Volume Decline": "🟠",
    }
    for _, row in flags_df.iterrows():
        icon = FLAG_ICONS.get(row["flag_type"], "⚪")
        with st.expander(f"{icon} {row['flag_type']} -- {row['program']} ({row['region']})"):
            st.write(row["recommendation"])

st.divider()
st.subheader("Strategic Priorities -- Q2 2026")
st.markdown("""
The following priorities are recommended for exec alignment at the next QBR, based on current portfolio performance:

**1. Address MEA adoption gap across all programs**
All four programs show below-portfolio-average adoption rates in MEA (82-84%), with USDC Settlement Rails missing volume OKR in the last quarter. This points to infrastructure and partner readiness gaps rather than product-market fit issues. Recommended action: commission a MEA Partner Readiness Assessment and allocate enablement resources before Q3.

**2. Accelerate USDC rail volume ramp in NA and EU**
USDC Settlement Rails is the highest-volume program but faces the steepest OKR stretch (10% above base). NA and EU partners represent 68% of total rail volume -- targeted onboarding support for the top 5 NA partners by volume would materially close the attainment gap without requiring rate concessions.

**3. Stabilise Crypto B2B Partnerships pipeline in LAC**
LAC shows consecutive month-over-month declines in partner adoption for Crypto B2B Partnerships. With only 3-4 active partners in the region, a single partner pause drives outsized metric swings. Recommended action: expand the LAC partner pipeline to at least 8 active partners as a buffer, and institute a 90-day onboarding SLA to sustain momentum.
""")
