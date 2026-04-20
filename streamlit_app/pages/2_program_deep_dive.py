import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from utils.data_loader import load_data

st.set_page_config(page_title="Program Deep-Dive", page_icon="🔍", layout="wide")

df = load_data()

PROGRAM_AVG_TXN = {
    "USDC Settlement Rails": 50_000,
    "Visa x Coinbase Card": 450,
    "Visa x Crypto.com Card": 380,
    "Crypto B2B Partnerships": 12_000,
}

st.title("Program Deep-Dive")
program = st.selectbox("Select Program", options=sorted(df["program"].unique()))

program_df = (
    df[df["program"] == program]
    .groupby("month")
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

program_df["okr_target"] = program_df["volume_usd"] / program_df["okr_attainment"]
program_df["band"] = program_df["okr_attainment"].apply(
    lambda x: "On Track" if x >= 0.90 else ("At Risk" if x >= 0.70 else "Miss")
)

st.divider()
st.subheader("Volume vs OKR Target")

volume_line = (
    alt.Chart(program_df)
    .mark_line(point=True, color="#1f77b4")
    .encode(
        x=alt.X("month:T", title="Month", axis=alt.Axis(format="%b %Y")),
        y=alt.Y("volume_usd:Q", title="Volume (USD)", axis=alt.Axis(format="$,.0f")),
        tooltip=[
            alt.Tooltip("month:T", format="%B %Y"),
            alt.Tooltip("volume_usd:Q", title="Actual Volume", format="$,.0f"),
        ],
    )
)
okr_line = (
    alt.Chart(program_df)
    .mark_line(strokeDash=[6, 3], color="#d62728")
    .encode(
        x="month:T",
        y=alt.Y("okr_target:Q"),
        tooltip=[alt.Tooltip("okr_target:Q", title="OKR Target", format="$,.0f")],
    )
)
st.altair_chart((volume_line + okr_line).properties(height=300), use_container_width=True)
st.caption("Solid line = Actual volume · Dashed red = OKR target")

st.divider()
st.subheader("OKR Attainment Over Time")

okr_chart = (
    alt.Chart(program_df)
    .mark_bar()
    .encode(
        x=alt.X("month:T", title="Month", axis=alt.Axis(format="%b %Y")),
        y=alt.Y("okr_attainment:Q", title="OKR Attainment", axis=alt.Axis(format=".0%")),
        color=alt.Color(
            "band:N",
            scale=alt.Scale(
                domain=["On Track", "At Risk", "Miss"],
                range=["#28a745", "#ffc107", "#dc3545"],
            ),
            title="Status",
        ),
        tooltip=[
            alt.Tooltip("month:T", format="%B %Y"),
            alt.Tooltip("okr_attainment:Q", title="OKR Attainment", format=".1%"),
            "band:N",
        ],
    )
    .properties(height=250)
)
st.altair_chart(okr_chart, use_container_width=True)

st.divider()
st.subheader("Partner Adoption by Region (Latest Month)")

latest_month = df["month"].max()
region_df = df[(df["program"] == program) & (df["month"] == latest_month)][
    ["region", "partner_adoption_rate", "active_partners"]
].sort_values("partner_adoption_rate", ascending=False)

adoption_chart = (
    alt.Chart(region_df)
    .mark_bar()
    .encode(
        y=alt.Y("region:N", sort="-x", title="Region"),
        x=alt.X("partner_adoption_rate:Q", title="Partner Adoption Rate", axis=alt.Axis(format=".0%")),
        color=alt.value("#4c78a8"),
        tooltip=[
            "region:N",
            alt.Tooltip("partner_adoption_rate:Q", title="Adoption Rate", format=".1%"),
            alt.Tooltip("active_partners:Q", title="Active Partners"),
        ],
    )
    .properties(height=220)
)
st.altair_chart(adoption_chart, use_container_width=True)

st.divider()
st.subheader("Settlement Efficiency Model")
st.caption(
    "Parametric cost model comparing Visa crypto rail vs traditional settlement. "
    "Traditional: 0.15% of volume. Crypto rail: $0.50/txn + 0.02% of volume."
)

avg_txn = PROGRAM_AVG_TXN[program]
volumes = np.linspace(10_000_000, 500_000_000, 200)
txn_counts = volumes / avg_txn

traditional_cost_pct = np.full_like(volumes, 0.15)
crypto_cost_pct = ((txn_counts * 0.50) + (volumes * 0.0002)) / volumes * 100

efficiency_df = pd.DataFrame({
    "volume_usd": np.concatenate([volumes, volumes]),
    "cost_pct": np.concatenate([traditional_cost_pct, crypto_cost_pct]),
    "rail": ["Traditional"] * len(volumes) + ["Crypto Rail"] * len(volumes),
})

latest_vol = float(program_df["volume_usd"].iloc[-1])
latest_txn = float(program_df["transaction_count"].iloc[-1])
current_crypto_pct = ((latest_txn * 0.50) + (latest_vol * 0.0002)) / latest_vol * 100
current_trad_pct = 0.15
current_point = pd.DataFrame({
    "volume_usd": [latest_vol, latest_vol],
    "cost_pct": [current_trad_pct, current_crypto_pct],
    "rail": ["Traditional", "Crypto Rail"],
})

cost_lines = (
    alt.Chart(efficiency_df)
    .mark_line()
    .encode(
        x=alt.X("volume_usd:Q", title="Monthly Volume (USD)", axis=alt.Axis(format="$,.0f")),
        y=alt.Y("cost_pct:Q", title="Settlement Cost (% of Volume)"),
        color=alt.Color("rail:N", title="Settlement Rail"),
        tooltip=[
            alt.Tooltip("volume_usd:Q", format="$,.0f", title="Volume"),
            alt.Tooltip("cost_pct:Q", format=".3f", title="Cost %"),
            "rail:N",
        ],
    )
)
current_dots = (
    alt.Chart(current_point)
    .mark_point(size=120, filled=True)
    .encode(
        x="volume_usd:Q",
        y="cost_pct:Q",
        color="rail:N",
        tooltip=[
            alt.Tooltip("volume_usd:Q", format="$,.0f", title="Current Volume"),
            alt.Tooltip("cost_pct:Q", format=".4f", title="Current Cost %"),
            "rail:N",
        ],
    )
)
st.altair_chart((cost_lines + current_dots).properties(height=300), use_container_width=True)

saving_pct = current_trad_pct - current_crypto_pct
if saving_pct > 0:
    st.success(
        f"At current volume, **{program}** saves **{saving_pct:.3f}%** of volume "
        f"(approx. ${latest_vol * saving_pct / 100:,.0f}/month) by settling on crypto rails vs traditional."
    )
else:
    st.warning(
        f"At current volume, **{program}** is above breakeven -- "
        "crypto rail costs exceed traditional settlement. Volume scale needed."
    )
