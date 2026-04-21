import altair as alt
import pandas as pd
import streamlit as st

from utils.data_loader import load_deals

st.set_page_config(page_title="Time to Revenue", page_icon="⏱️", layout="wide")

_STAGE_ORDER = ["Intake", "Onboarding", "Certification", "Activation", "Live"]
_STAGE_THRESHOLD = {"Intake": 5, "Onboarding": 10, "Certification": 14, "Activation": 7}

df = load_deals()
post_sale = df[df["is_post_sale"]].copy()

st.title("Post-Sale Time-to-Revenue")
st.caption("Stage funnel, cycle time analysis, and bottleneck identification · NA VAS")

total_post_sale = len(post_sale)
live_count = int((post_sale["stage"] == "Live").sum())
ttr_series = post_sale["days_to_first_revenue"].dropna()
avg_ttr = ttr_series.mean() if len(ttr_series) > 0 else float("nan")
stalled = int(
    post_sale.apply(
        lambda r: r["days_in_current_stage"] > _STAGE_THRESHOLD.get(r["stage"], 999),
        axis=1,
    ).sum()
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Post-Sale Deals", total_post_sale)
col2.metric("Live (Revenue Active)", live_count)
col3.metric(
    "Avg Days to First Revenue",
    f"{avg_ttr:.0f} days" if not pd.isna(avg_ttr) else "N/A",
)
col4.metric(
    "Stalled Deals",
    stalled,
    delta=f"{stalled / total_post_sale:.0%} of post-sale" if total_post_sale else "0%",
    delta_color="inverse",
)

st.divider()
st.subheader("Post-Sale Stage Funnel")

funnel_df = (
    post_sale.groupby("stage")
    .size()
    .reindex(_STAGE_ORDER, fill_value=0)
    .reset_index(name="deal_count")
)
funnel_df["stage"] = pd.Categorical(funnel_df["stage"], categories=_STAGE_ORDER, ordered=True)

funnel_chart = (
    alt.Chart(funnel_df)
    .mark_bar()
    .encode(
        x=alt.X("deal_count:Q", title="Number of Deals"),
        y=alt.Y("stage:N", sort=_STAGE_ORDER, title="Stage"),
        color=alt.Color("deal_count:Q", scale=alt.Scale(scheme="blues"), legend=None),
        tooltip=["stage:N", "deal_count:Q"],
    )
    .properties(height=220)
)
st.altair_chart(funnel_chart, use_container_width=True)

st.divider()
st.subheader("Avg Cycle Time per Stage")

active_stages = [s for s in _STAGE_ORDER if s != "Live"]
cycle_df = (
    post_sale[post_sale["stage"].isin(active_stages)]
    .groupby("stage")
    .agg(avg_days=("days_in_current_stage", "mean"))
    .reindex(active_stages)
    .reset_index()
)
cycle_df["threshold"] = cycle_df["stage"].map(_STAGE_THRESHOLD)
cycle_df["status"] = cycle_df.apply(
    lambda r: "Bottleneck" if r["avg_days"] > r["threshold"] else "On Track", axis=1
)

cycle_chart = (
    alt.Chart(cycle_df)
    .mark_bar()
    .encode(
        x=alt.X("stage:N", sort=active_stages, title="Stage"),
        y=alt.Y("avg_days:Q", title="Avg Days in Stage"),
        color=alt.Color(
            "status:N",
            scale=alt.Scale(domain=["Bottleneck", "On Track"], range=["#dc3545", "#28a745"]),
            title="Status",
        ),
        tooltip=[
            "stage:N",
            alt.Tooltip("avg_days:Q", title="Avg Days", format=".1f"),
            "status:N",
        ],
    )
    .properties(height=280)
)
st.altair_chart(cycle_chart, use_container_width=True)

st.divider()
st.subheader("Days to First Revenue by Product")
st.caption("Distribution of days from Closed Won to first Live revenue")

live_df = post_sale[post_sale["days_to_first_revenue"].notna()].copy()

if len(live_df) > 0:
    ttr_chart = (
        alt.Chart(live_df)
        .mark_boxplot(extent="min-max")
        .encode(
            x=alt.X("product:N", title="Product"),
            y=alt.Y("days_to_first_revenue:Q", title="Days to First Revenue"),
            color=alt.Color("product:N", legend=None),
        )
        .properties(height=280)
    )
    st.altair_chart(ttr_chart, use_container_width=True)
else:
    st.info("No Live deals with revenue data yet.")
