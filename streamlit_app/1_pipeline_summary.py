import altair as alt
import pandas as pd
import streamlit as st

from utils.data_loader import load_pipeline_monthly
from utils.deal_health import compute_deal_health

st.set_page_config(page_title="Visa VAS Pipeline", page_icon="💳", layout="wide")

df = load_pipeline_monthly()

monthly = (
    df.groupby(["month", "product"])
    .agg(
        pipeline_value_usd=("pipeline_value_usd", "sum"),
        avg_deal_size_usd=("avg_deal_size_usd", "mean"),
        win_rate=("win_rate", "mean"),
        avg_days_to_close=("avg_days_to_close", "mean"),
        mom_growth=("mom_growth", "mean"),
    )
    .reset_index()
)

sorted_months = sorted(monthly["month"].unique())
latest_month = sorted_months[-1]
prev_month = sorted_months[-2] if len(sorted_months) >= 2 else sorted_months[-1]
latest = monthly[monthly["month"] == latest_month]
prev = monthly[monthly["month"] == prev_month]

total_pipeline = latest["pipeline_value_usd"].sum()
prev_pipeline = prev["pipeline_value_usd"].sum()
blended_win_rate = latest["win_rate"].mean()
avg_days = latest["avg_days_to_close"].mean()
portfolio_growth = latest["mom_growth"].mean()

st.title("Visa Acceptance Solutions — Executive Pipeline Summary")
st.caption(
    f"As of {pd.Timestamp(latest_month).strftime('%B %Y')} · NA VAS Sales Enablement"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Total Pipeline Value",
    f"${total_pipeline / 1e6:.1f}M",
    delta=f"{(total_pipeline - prev_pipeline) / prev_pipeline:.1%} MoM",
)
col2.metric("Blended Win Rate", f"{blended_win_rate:.0%}")
col3.metric("Avg Days to Close", f"{avg_days:.0f} days")
col4.metric("Pipeline MoM Growth", f"{portfolio_growth:.1%}")

st.divider()
st.subheader("Pipeline Value by Product (Last 12 Months)")

cutoff = sorted_months[-12] if len(sorted_months) >= 12 else sorted_months[0]
trend_df = monthly[monthly["month"] >= cutoff].copy()
trend_df["pipeline_m"] = trend_df["pipeline_value_usd"] / 1e6

chart = (
    alt.Chart(trend_df)
    .mark_line(point=True)
    .encode(
        x=alt.X("month:T", title="Month", axis=alt.Axis(format="%b %Y")),
        y=alt.Y("pipeline_m:Q", title="Pipeline Value ($M)", axis=alt.Axis(format="$,.1f")),
        color=alt.Color("product:N", title="Product"),
        tooltip=[
            alt.Tooltip("month:T", title="Month", format="%B %Y"),
            "product:N",
            alt.Tooltip("pipeline_m:Q", title="Pipeline ($M)", format="$,.2f"),
        ],
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)

st.divider()
st.subheader("Deal Health Scorecard")

BAND_COLORS = {"Strong": "#d4edda", "Moderate": "#fff3cd", "At Risk": "#f8d7da"}

scorecard_rows = []
for _, row in latest.iterrows():
    score, band = compute_deal_health(
        row["win_rate"], row["avg_days_to_close"], row["mom_growth"]
    )
    scorecard_rows.append({
        "Product": row["product"],
        "Health Score": score,
        "Band": band,
        "Win Rate": f"{row['win_rate']:.0%}",
        "Avg Deal Size": f"${row['avg_deal_size_usd'] / 1e3:.0f}K",
        "Avg Days to Close": f"{row['avg_days_to_close']:.0f}",
        "MoM Growth": f"{row['mom_growth']:+.1%}",
    })

scorecard_df = (
    pd.DataFrame(scorecard_rows).sort_values("Health Score", ascending=False)
)


def _color_band(val: str) -> str:
    return f"background-color: {BAND_COLORS.get(val, '')}"


st.dataframe(
    scorecard_df.style.map(_color_band, subset=["Band"]),
    use_container_width=True,
    hide_index=True,
)
