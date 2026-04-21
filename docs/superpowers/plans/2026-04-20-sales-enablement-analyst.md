# Sales Enablement AI Solutions Analyst Dashboard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 4-page Streamlit dashboard demonstrating the core skills of Visa's Sales Enablement AI Solutions Analyst role — pipeline analytics, velocity modelling, post-sale time-to-revenue tracking, and an AI-powered deal recommendation engine.

**Architecture:** Two synthetic CSVs feed four Streamlit pages via cached loaders. Two pure functions (`compute_deal_health`, `compute_ai_recommendations`) carry all scoring and flagging logic, keeping them fully unit-testable with no Streamlit dependency. Pages import from `utils/` and render with Altair charts.

**Tech Stack:** Python 3.10+, Streamlit, Pandas, Altair, pytest

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Delete | `streamlit_app/1_portfolio_summary.py` | Old crypto page — replaced |
| Delete | `streamlit_app/pages/2_program_deep_dive.py` | Old crypto page |
| Delete | `streamlit_app/pages/3_risk_recommendations.py` | Old crypto page |
| Delete | `streamlit_app/utils/health_score.py` | Old crypto util |
| Delete | `streamlit_app/utils/risk_flags.py` | Old crypto util |
| Delete | `streamlit_app/data/crypto_programs.csv` | Old crypto data |
| Delete | `tests/test_health_score.py` | Old crypto tests |
| Delete | `tests/test_risk_flags.py` | Old crypto tests |
| Create | `streamlit_app/generate_data.py` | Generates both CSVs |
| Create | `streamlit_app/data/pipeline_monthly.csv` | 288 rows: monthly aggregates by product × segment |
| Create | `streamlit_app/data/deals.csv` | 200 rows: individual deal snapshot |
| Replace | `streamlit_app/utils/data_loader.py` | `load_pipeline_monthly()` and `load_deals()` |
| Create | `streamlit_app/utils/deal_health.py` | `compute_deal_health()` pure function |
| Create | `streamlit_app/utils/ai_recommendations.py` | `compute_ai_recommendations()` pure function |
| Create | `streamlit_app/1_pipeline_summary.py` | Page 1 — Executive Pipeline Summary |
| Create | `streamlit_app/pages/2_pipeline_velocity.py` | Page 2 — Pipeline Velocity Model |
| Create | `streamlit_app/pages/3_time_to_revenue.py` | Page 3 — Post-Sale Time-to-Revenue |
| Create | `streamlit_app/pages/4_ai_insight_engine.py` | Page 4 — AI Insight Engine |
| Create | `tests/test_deal_health.py` | Unit tests for compute_deal_health |
| Create | `tests/test_ai_recommendations.py` | Unit tests for compute_ai_recommendations |
| Replace | `README.md` | Updated for new role and dashboard |

---

### Task 1: Remove old crypto files

**Files:**
- Delete: `streamlit_app/1_portfolio_summary.py`
- Delete: `streamlit_app/pages/2_program_deep_dive.py`
- Delete: `streamlit_app/pages/3_risk_recommendations.py`
- Delete: `streamlit_app/utils/health_score.py`
- Delete: `streamlit_app/utils/risk_flags.py`
- Delete: `streamlit_app/data/crypto_programs.csv`
- Delete: `tests/test_health_score.py`
- Delete: `tests/test_risk_flags.py`

- [ ] **Step 1: Delete old files**

```bash
git rm streamlit_app/1_portfolio_summary.py \
       streamlit_app/pages/2_program_deep_dive.py \
       streamlit_app/pages/3_risk_recommendations.py \
       streamlit_app/utils/health_score.py \
       streamlit_app/utils/risk_flags.py \
       streamlit_app/data/crypto_programs.csv \
       tests/test_health_score.py \
       tests/test_risk_flags.py
```

- [ ] **Step 2: Verify git status shows only deletions**

```bash
git status
```

Expected: 8 deleted files staged, nothing else.

- [ ] **Step 3: Commit**

```bash
git commit -m "chore: remove crypto analyst pages, utils, and data"
```

---

### Task 2: Generate synthetic data

**Files:**
- Create: `streamlit_app/generate_data.py`
- Create: `streamlit_app/data/pipeline_monthly.csv` (output)
- Create: `streamlit_app/data/deals.csv` (output)

- [ ] **Step 1: Write generate_data.py**

`streamlit_app/generate_data.py`:

```python
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
```

- [ ] **Step 2: Run the generator and verify output**

```bash
cd streamlit_app && python generate_data.py
```

Expected output:
```
pipeline_monthly.csv: 288 rows
deals.csv: 200 rows
```

- [ ] **Step 3: Spot-check the CSVs**

```bash
python -c "
import pandas as pd
pm = pd.read_csv('data/pipeline_monthly.csv')
d = pd.read_csv('data/deals.csv')
print('pipeline_monthly columns:', list(pm.columns))
print('pipeline_monthly shape:', pm.shape)
print('deals columns:', list(d.columns))
print('deals shape:', d.shape)
print('post_sale split:', d['is_post_sale'].value_counts().to_dict())
print('stages:', d['stage'].value_counts().to_dict())
"
```

Expected: 288 rows × 10 cols for pipeline_monthly, 200 rows × 10 cols for deals, both True and False in `is_post_sale`.

- [ ] **Step 4: Commit**

```bash
cd ..
git add streamlit_app/generate_data.py streamlit_app/data/pipeline_monthly.csv streamlit_app/data/deals.csv
git commit -m "feat: add synthetic data generator and CSV datasets"
```

---

### Task 3: Replace data loader

**Files:**
- Modify: `streamlit_app/utils/data_loader.py`

- [ ] **Step 1: Replace data_loader.py**

`streamlit_app/utils/data_loader.py`:

```python
import pandas as pd
import streamlit as st
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"


@st.cache_data
def load_pipeline_monthly() -> pd.DataFrame:
    return pd.read_csv(_DATA_DIR / "pipeline_monthly.csv", parse_dates=["month"])


@st.cache_data
def load_deals() -> pd.DataFrame:
    return pd.read_csv(_DATA_DIR / "deals.csv")
```

- [ ] **Step 2: Commit**

```bash
git add streamlit_app/utils/data_loader.py
git commit -m "feat: update data loader for pipeline_monthly and deals CSVs"
```

---

### Task 4: Implement compute_deal_health (TDD)

**Files:**
- Create: `streamlit_app/utils/deal_health.py`
- Create: `tests/test_deal_health.py`

Score formula:
- `days_score = max(0.0, 1.0 - avg_days_to_close / 180.0)`
- `growth_score = min(1.0, max(0.0, (mom_growth + 0.1) / 0.2))`
- `score = win_rate * 45.0 + growth_score * 30.0 + days_score * 25.0`
- Band: `Strong` ≥ 70, `Moderate` ≥ 40, `At Risk` < 40

- [ ] **Step 1: Write the failing tests**

`tests/test_deal_health.py`:

```python
from utils.deal_health import compute_deal_health


def test_strong_inputs_return_strong_band():
    score, band = compute_deal_health(win_rate=0.9, avg_days_to_close=30.0, mom_growth=0.1)
    assert band == "Strong"
    assert score >= 70


def test_weak_inputs_return_at_risk_band():
    score, band = compute_deal_health(win_rate=0.1, avg_days_to_close=180.0, mom_growth=-0.1)
    assert band == "At Risk"
    assert score < 40


def test_moderate_inputs_return_moderate_band():
    # win=0.4 → 18, growth=0 → 15, days=90 → 12.5  total=45.5
    score, band = compute_deal_health(win_rate=0.4, avg_days_to_close=90.0, mom_growth=0.0)
    assert band == "Moderate"
    assert 40 <= score < 70


def test_win_rate_dominates_weighting():
    # High win rate, slow close, slight decline
    score_high_win, _ = compute_deal_health(win_rate=0.9, avg_days_to_close=120.0, mom_growth=-0.05)
    # Low win rate, fast close, positive growth
    score_low_win, _ = compute_deal_health(win_rate=0.1, avg_days_to_close=30.0, mom_growth=0.1)
    assert score_high_win > score_low_win


def test_score_clamped_to_100_on_perfect_inputs():
    score, _ = compute_deal_health(win_rate=1.0, avg_days_to_close=0.0, mom_growth=1.0)
    assert score == 100.0


def test_score_floored_at_zero_on_worst_inputs():
    score, _ = compute_deal_health(win_rate=0.0, avg_days_to_close=999.0, mom_growth=-1.0)
    assert score == 0.0
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_deal_health.py -v
```

Expected: 6 errors — `ModuleNotFoundError: No module named 'utils.deal_health'`

- [ ] **Step 3: Implement compute_deal_health**

`streamlit_app/utils/deal_health.py`:

```python
def compute_deal_health(
    win_rate: float,
    avg_days_to_close: float,
    mom_growth: float,
) -> tuple[float, str]:
    days_score = max(0.0, 1.0 - avg_days_to_close / 180.0)
    growth_score = min(1.0, max(0.0, (mom_growth + 0.1) / 0.2))
    score = win_rate * 45.0 + growth_score * 30.0 + days_score * 25.0
    score = round(min(100.0, max(0.0, score)), 1)
    band = "Strong" if score >= 70 else ("Moderate" if score >= 40 else "At Risk")
    return score, band
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_deal_health.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add streamlit_app/utils/deal_health.py tests/test_deal_health.py
git commit -m "feat: add compute_deal_health with unit tests"
```

---

### Task 5: Implement compute_ai_recommendations (TDD)

**Files:**
- Create: `streamlit_app/utils/ai_recommendations.py`
- Create: `tests/test_ai_recommendations.py`

Flag rules:
- Post-sale `days_in_current_stage > 14` → `Critical`, `flag_type = "post_sale_stall"`
- Post-sale stage in `("Onboarding", "Certification")` and `days > 10` (and ≤ 14) → `Warning`, `flag_type = "onboarding_cert_delay"`
- Pre-sale `days > 21` → `Warning`, `flag_type = "pre_sale_stall"`
- Pre-sale `days > 14` (and ≤ 21) → `Watch`, `flag_type = "pre_sale_approaching"`

- [ ] **Step 1: Write the failing tests**

`tests/test_ai_recommendations.py`:

```python
import pandas as pd
from utils.ai_recommendations import compute_ai_recommendations


def _deal(deal_id, product, segment, acquirer_name, stage, days_in_stage, is_post_sale):
    return {
        "deal_id": deal_id,
        "product": product,
        "acquirer_segment": segment,
        "acquirer_name": acquirer_name,
        "deal_value_usd": 100_000.0,
        "stage": stage,
        "days_in_current_stage": days_in_stage,
        "total_days_in_flight": days_in_stage,
        "is_post_sale": is_post_sale,
        "days_to_first_revenue": None,
    }


def test_post_sale_over_14_days_is_critical():
    df = pd.DataFrame([_deal("VAS-0001", "Tap-to-Phone", "ISOs", "Paysafe", "Certification", 20, True)])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 1
    assert flags[0]["severity"] == "Critical"
    assert flags[0]["flag_type"] == "post_sale_stall"


def test_onboarding_between_10_and_14_days_is_warning():
    df = pd.DataFrame([_deal("VAS-0002", "Tokenization Suite", "Fintechs", "Stripe", "Onboarding", 12, True)])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 1
    assert flags[0]["severity"] == "Warning"
    assert flags[0]["flag_type"] == "onboarding_cert_delay"


def test_pre_sale_over_21_days_is_warning():
    df = pd.DataFrame([_deal("VAS-0003", "Acceptance API", "Regional Banks", "First National Bank", "Proposal", 25, False)])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 1
    assert flags[0]["severity"] == "Warning"
    assert flags[0]["flag_type"] == "pre_sale_stall"


def test_pre_sale_between_14_and_21_days_is_watch():
    df = pd.DataFrame([_deal("VAS-0004", "Visa Acceptance Console", "Tier 1 Banks", "JPMorgan Chase", "Negotiation", 17, False)])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 1
    assert flags[0]["severity"] == "Watch"
    assert flags[0]["flag_type"] == "pre_sale_approaching"


def test_healthy_deal_produces_no_flags():
    df = pd.DataFrame([_deal("VAS-0005", "Tap-to-Phone", "ISOs", "Cayan", "Onboarding", 5, True)])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 0


def test_next_best_action_non_empty_for_every_flag():
    df = pd.DataFrame([
        _deal("VAS-0006", "Tap-to-Phone", "ISOs", "Paysafe", "Certification", 20, True),
        _deal("VAS-0007", "Acceptance API", "Fintechs", "Adyen", "Proposal", 30, False),
    ])
    flags = compute_ai_recommendations(df)
    assert len(flags) == 2
    assert all(len(f["next_best_action"]) > 0 for f in flags)
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_ai_recommendations.py -v
```

Expected: 6 errors — `ModuleNotFoundError: No module named 'utils.ai_recommendations'`

- [ ] **Step 3: Implement compute_ai_recommendations**

`streamlit_app/utils/ai_recommendations.py`:

```python
import pandas as pd

_POST_SALE_STALL = 14
_ONBOARDING_CERT_WATCH = 10
_PRE_SALE_STALL = 21
_PRE_SALE_WATCH = 14


def compute_ai_recommendations(deals_df: pd.DataFrame) -> list[dict]:
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
```

- [ ] **Step 4: Run all tests to confirm they pass**

```bash
pytest -v
```

Expected: 12 passed.

- [ ] **Step 5: Commit**

```bash
git add streamlit_app/utils/ai_recommendations.py tests/test_ai_recommendations.py
git commit -m "feat: add compute_ai_recommendations with unit tests"
```

---

### Task 6: Page 1 — Executive Pipeline Summary

**Files:**
- Create: `streamlit_app/1_pipeline_summary.py`

- [ ] **Step 1: Create 1_pipeline_summary.py**

`streamlit_app/1_pipeline_summary.py`:

```python
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
```

- [ ] **Step 2: Run the Streamlit app and verify Page 1 renders**

```bash
cd streamlit_app && streamlit run 1_pipeline_summary.py
```

Check: 4 KPI cards visible, line chart renders with 4 product lines, health scorecard table shows 4 rows with colour-coded bands.

- [ ] **Step 3: Commit**

```bash
cd ..
git add streamlit_app/1_pipeline_summary.py
git commit -m "feat: add Page 1 Executive Pipeline Summary"
```

---

### Task 7: Page 2 — Pipeline Velocity Model

**Files:**
- Create: `streamlit_app/pages/2_pipeline_velocity.py`

- [ ] **Step 1: Create 2_pipeline_velocity.py**

`streamlit_app/pages/2_pipeline_velocity.py`:

```python
import altair as alt
import pandas as pd
import streamlit as st

from utils.data_loader import load_pipeline_monthly

st.set_page_config(page_title="Pipeline Velocity", page_icon="📈", layout="wide")

df = load_pipeline_monthly()
products = sorted(df["product"].unique())
segments = sorted(df["acquirer_segment"].unique())

st.title("Pipeline Velocity Model")
st.caption(
    "Win rate, deal cycle time, and deal size dynamics across VAS products and acquirer segments"
)

col_f1, col_f2 = st.columns(2)
selected_product = col_f1.selectbox("Product", ["All"] + products)
selected_segments = col_f2.multiselect("Acquirer Segments", segments, default=segments)

filtered = df.copy()
if selected_product != "All":
    filtered = filtered[filtered["product"] == selected_product]
if selected_segments:
    filtered = filtered[filtered["acquirer_segment"].isin(selected_segments)]

monthly = (
    filtered.groupby(["month", "acquirer_segment"])
    .agg(
        win_rate=("win_rate", "mean"),
        avg_days_to_close=("avg_days_to_close", "mean"),
        avg_deal_size_usd=("avg_deal_size_usd", "mean"),
        pipeline_value_usd=("pipeline_value_usd", "sum"),
    )
    .reset_index()
)

sorted_months = sorted(monthly["month"].unique())
cutoff = sorted_months[-12] if len(sorted_months) >= 12 else sorted_months[0]
trend_df = monthly[monthly["month"] >= cutoff].copy()

st.divider()
st.subheader("Win Rate Over Time by Segment")

win_chart = (
    alt.Chart(trend_df)
    .mark_bar()
    .encode(
        x=alt.X("month:T", title="Month", axis=alt.Axis(format="%b %Y")),
        y=alt.Y("win_rate:Q", title="Win Rate", axis=alt.Axis(format=".0%")),
        color=alt.Color("acquirer_segment:N", title="Segment"),
        xOffset="acquirer_segment:N",
        tooltip=[
            alt.Tooltip("month:T", title="Month", format="%B %Y"),
            "acquirer_segment:N",
            alt.Tooltip("win_rate:Q", title="Win Rate", format=".1%"),
        ],
    )
    .properties(height=280)
)
st.altair_chart(win_chart, use_container_width=True)

st.divider()
st.subheader("Avg Days to Close by Segment (Last 3 Months)")

last3 = sorted_months[-3:]
days_df = (
    monthly[monthly["month"].isin(last3)]
    .groupby("acquirer_segment")
    .agg(avg_days=("avg_days_to_close", "mean"))
    .reset_index()
    .sort_values("avg_days")
)

days_chart = (
    alt.Chart(days_df)
    .mark_bar()
    .encode(
        x=alt.X("avg_days:Q", title="Avg Days to Close"),
        y=alt.Y("acquirer_segment:N", title="Segment", sort="-x"),
        color=alt.Color("acquirer_segment:N", legend=None),
        tooltip=[
            "acquirer_segment:N",
            alt.Tooltip("avg_days:Q", title="Avg Days", format=".1f"),
        ],
    )
    .properties(height=200)
)
st.altair_chart(days_chart, use_container_width=True)

st.divider()
st.subheader("Deal Size vs Win Rate by Segment")
st.caption(
    "Bubble size = pipeline value. ISOs close faster at lower deal size; "
    "Tier 1 Banks carry higher value but longer cycles."
)

scatter_df = (
    filtered.groupby("acquirer_segment")
    .agg(
        avg_deal_size_usd=("avg_deal_size_usd", "mean"),
        win_rate=("win_rate", "mean"),
        pipeline_value_usd=("pipeline_value_usd", "sum"),
    )
    .reset_index()
)
scatter_df["deal_size_k"] = scatter_df["avg_deal_size_usd"] / 1e3

scatter_chart = (
    alt.Chart(scatter_df)
    .mark_circle()
    .encode(
        x=alt.X("deal_size_k:Q", title="Avg Deal Size ($K)", axis=alt.Axis(format="$,.0f")),
        y=alt.Y("win_rate:Q", title="Win Rate", axis=alt.Axis(format=".0%")),
        size=alt.Size("pipeline_value_usd:Q", title="Pipeline Value", legend=None),
        color=alt.Color("acquirer_segment:N", title="Segment"),
        tooltip=[
            "acquirer_segment:N",
            alt.Tooltip("deal_size_k:Q", title="Avg Deal Size ($K)", format="$,.0f"),
            alt.Tooltip("win_rate:Q", title="Win Rate", format=".1%"),
            alt.Tooltip("pipeline_value_usd:Q", title="Pipeline Value", format="$,.0f"),
        ],
    )
    .properties(height=300)
)
st.altair_chart(scatter_chart, use_container_width=True)
```

- [ ] **Step 2: Open the running app and verify Page 2**

Navigate to Page 2 in the sidebar.

Check: product dropdown and segment multiselect filter the charts, win rate bar chart groups by segment, days-to-close horizontal bar renders, scatter shows 4 bubbles sized by pipeline value.

- [ ] **Step 3: Commit**

```bash
git add streamlit_app/pages/2_pipeline_velocity.py
git commit -m "feat: add Page 2 Pipeline Velocity Model"
```

---

### Task 8: Page 3 — Post-Sale Time-to-Revenue

**Files:**
- Create: `streamlit_app/pages/3_time_to_revenue.py`

- [ ] **Step 1: Create 3_time_to_revenue.py**

`streamlit_app/pages/3_time_to_revenue.py`:

```python
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
```

- [ ] **Step 2: Open the app and verify Page 3**

Navigate to Page 3.

Check: 4 KPI cards render, funnel horizontal bar shows 5 stages, cycle time bar chart highlights bottleneck stages in red, box-plot shows distribution by product (if Live deals exist).

- [ ] **Step 3: Commit**

```bash
git add streamlit_app/pages/3_time_to_revenue.py
git commit -m "feat: add Page 3 Post-Sale Time-to-Revenue with bottleneck flagging"
```

---

### Task 9: Page 4 — AI Insight Engine

**Files:**
- Create: `streamlit_app/pages/4_ai_insight_engine.py`

- [ ] **Step 1: Create 4_ai_insight_engine.py**

`streamlit_app/pages/4_ai_insight_engine.py`:

```python
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
```

- [ ] **Step 2: Open the app and verify Page 4**

Navigate to Page 4.

Check: 4 severity KPI cards render, recommendations table shows colour-coded severity rows (Critical red, Warning yellow, Watch blue), Strategic Priorities section renders 3 bullet points.

- [ ] **Step 3: Run full test suite one final time**

```bash
cd .. && pytest -v
```

Expected: 12 passed.

- [ ] **Step 4: Commit**

```bash
git add streamlit_app/pages/4_ai_insight_engine.py
git commit -m "feat: add Page 4 AI Insight Engine with deal recommendations"
```

---

### Task 10: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace README.md**

`README.md`:

```markdown
# Visa NA VAS — Sales Enablement AI Solutions Analyst

This project models the analytical and AI automation work performed by a Sales Enablement
AI Solutions Analyst on Visa's North America Visa Acceptance Solutions (NA VAS) team.
It synthesises two datasets — 288 rows of monthly pipeline data across 4 VAS products
and 4 acquirer segments, and 200 individual deal snapshots — to demonstrate pipeline
health tracking, velocity analysis, post-sale time-to-revenue monitoring, and an
automated AI deal recommendation engine.

## Live Dashboard

**URL:** *(add Streamlit Community Cloud URL after deployment)*

## Job Posting

- **Role:** Sales Enablement AI Solutions Analyst
- **Company:** Visa Inc. — NA VAS (North America Visa Acceptance Solutions)

## Tech Stack

| Layer | Tool |
|---|---|
| Data | Two synthesized CSVs — Python generator script |
| Data Processing | Pandas |
| Scoring Model | Python pure functions (`compute_deal_health`, `compute_ai_recommendations`) |
| Visualisation | Altair |
| Dashboard | Streamlit (four-page multipage app) |
| Testing | pytest (12 unit tests) |
| Deployment | Streamlit Community Cloud |

## Dashboard Pages

**Page 1 — Executive Pipeline Summary:** Portfolio KPI cards (pipeline value, win rate,
days to close, MoM growth), 12-month pipeline trend by VAS product, and a colour-coded
Deal Health Scorecard ranking all four products.

**Page 2 — Pipeline Velocity Model:** Product and segment filters, win rate over time by
segment, average days-to-close comparison, and a centrepiece deal-size vs. win-rate
scatter showing where to prioritise GTM effort.

**Page 3 — Post-Sale Time-to-Revenue:** Post-sale stage funnel, average cycle time per
stage with bottleneck flagging (red = exceeds threshold), and a box-plot distribution
of days from Closed Won to first Live revenue by product.

**Page 4 — AI Insight Engine:** Automated deal monitoring that surfaces stalled deals
and generates exec-ready next-best-action recommendations. Severity-coded (Critical /
Warning / Watch) with a Strategic Priorities QBR section.

## Key Insights

**Pipeline health:** Tokenization Suite leads on deal health score driven by the highest
average deal size and consistent MoM growth. ISOs show the highest win rate but smallest
deal size — strong volume lever, limited revenue concentration.

**Velocity:** Tier 1 Banks take 3x longer to close than ISOs but carry 9x the deal value.
GTM prioritisation should balance ISO volume velocity against Tier 1 revenue concentration
based on quarterly pipeline targets.

**Time-to-revenue:** Certification is the longest post-sale stage across all products —
the primary bottleneck between Closed Won and first revenue. A readiness checklist
deployed at Intake is the highest-leverage intervention.

**AI flags:** The recommendation engine surfaces Critical flags (post-sale stalls >14 days)
and Warning flags (pre-sale stalls >21 days or Onboarding/Certification delays >10 days),
automating the manual deal-review work that would otherwise require daily CRM triage.

## Setup & Reproduction

**Requirements:** Python 3.10+

```bash
pip install streamlit altair pandas numpy pytest

# Run the dashboard (from streamlit_app/)
cd streamlit_app
streamlit run 1_pipeline_summary.py

# Run tests (from project root)
pytest

# Regenerate datasets
cd streamlit_app
python generate_data.py
```

## Repository Structure

    .
    ├── streamlit_app/
    │   ├── 1_pipeline_summary.py          # Page 1: Executive Pipeline Summary
    │   ├── pages/
    │   │   ├── 2_pipeline_velocity.py     # Page 2: Velocity Model + segment scatter
    │   │   ├── 3_time_to_revenue.py       # Page 3: Post-sale funnel + bottleneck flags
    │   │   └── 4_ai_insight_engine.py     # Page 4: AI recommendations + QBR priorities
    │   ├── utils/
    │   │   ├── data_loader.py             # Cached loaders for both CSVs
    │   │   ├── deal_health.py             # compute_deal_health() pure function
    │   │   └── ai_recommendations.py      # compute_ai_recommendations() pure function
    │   ├── data/
    │   │   ├── pipeline_monthly.csv       # 288 rows monthly pipeline data
    │   │   └── deals.csv                  # 200 rows deal-level snapshot
    │   └── generate_data.py               # Synthetic data generator
    ├── tests/
    │   ├── test_deal_health.py            # 6 unit tests
    │   └── test_ai_recommendations.py     # 6 unit tests
    ├── pytest.ini
    └── README.md
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README for Sales Enablement AI Solutions Analyst dashboard"
```
