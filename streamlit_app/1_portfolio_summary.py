import streamlit as st
import altair as alt
import pandas as pd
from utils.data_loader import load_data
from utils.health_score import compute_health_score

st.set_page_config(page_title="Visa Crypto Portfolio", page_icon="💳", layout="wide")

df = load_data()

monthly = (
    df.groupby(["month", "program"])
    .agg(
        volume_usd=("volume_usd", "sum"),
        transaction_count=("transaction_count", "sum"),
        active_partners=("active_partners", "sum"),
        okr_attainment=("okr_attainment", "mean"),
        mom_growth=("mom_growth", "mean"),
        partner_adoption_rate=("partner_adoption_rate", "mean"),
    )
    .reset_index()
)

latest_month = monthly["month"].max()
latest = monthly[monthly["month"] == latest_month]

sorted_months = sorted(monthly["month"].unique())
prev_month = sorted_months[-2] if len(sorted_months) >= 2 else sorted_months[-1]
prev = monthly[monthly["month"] == prev_month]

total_volume = latest["volume_usd"].sum()
prev_volume = prev["volume_usd"].sum()
blended_okr = latest["okr_attainment"].mean()
portfolio_growth = latest["mom_growth"].mean()
total_partners = int(latest["active_partners"].sum())

st.title("Visa Crypto Portfolio -- Executive Summary")
st.caption(f"As of {pd.Timestamp(latest_month).strftime('%B %Y')} · Growth Products & Partnerships")

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Total Portfolio Volume",
    f"${total_volume / 1e9:.2f}B",
    delta=f"{(total_volume - prev_volume) / prev_volume:.1%} MoM",
)
col2.metric("Blended OKR Attainment", f"{blended_okr:.0%}")
col3.metric("Portfolio MoM Growth", f"{portfolio_growth:.1%}")
col4.metric("Total Active Partners", f"{total_partners:,}")

st.divider()
st.subheader("Volume Trend by Program (Last 12 Months)")

cutoff = sorted_months[-12] if len(sorted_months) >= 12 else sorted_months[0]
trend_df = monthly[monthly["month"] >= cutoff].copy()
trend_df["volume_b"] = trend_df["volume_usd"] / 1e9

chart = (
    alt.Chart(trend_df)
    .mark_line(point=True)
    .encode(
        x=alt.X("month:T", title="Month", axis=alt.Axis(format="%b %Y")),
        y=alt.Y("volume_b:Q", title="Volume (USD Billions)", axis=alt.Axis(format="$.2f")),
        color=alt.Color("program:N", title="Program"),
        tooltip=[
            alt.Tooltip("month:T", title="Month", format="%B %Y"),
            "program:N",
            alt.Tooltip("volume_b:Q", title="Volume ($B)", format="$.3f"),
        ],
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)

st.divider()
st.subheader("Program Health Scorecard")

scorecard_rows = []
for _, row in latest.iterrows():
    score, band = compute_health_score(
        row["okr_attainment"], row["mom_growth"], row["partner_adoption_rate"]
    )
    scorecard_rows.append({
        "Program": row["program"],
        "Health Score": score,
        "Band": band,
        "OKR Attainment": f"{row['okr_attainment']:.0%}",
        "Partner Adoption": f"{row['partner_adoption_rate']:.0%}",
        "MoM Growth": f"{row['mom_growth']:+.1%}",
        "Volume ($B)": f"${row['volume_usd'] / 1e9:.3f}",
    })

scorecard_df = pd.DataFrame(scorecard_rows).sort_values("Health Score", ascending=False)

BAND_COLORS = {"High": "#d4edda", "Medium": "#fff3cd", "Low": "#f8d7da"}


def _color_band(val):
    return f"background-color: {BAND_COLORS.get(val, '')}"


st.dataframe(
    scorecard_df.style.map(_color_band, subset=["Band"]),
    use_container_width=True,
    hide_index=True,
)
