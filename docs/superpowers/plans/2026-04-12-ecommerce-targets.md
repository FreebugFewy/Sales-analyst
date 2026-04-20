# E-commerce Merchant Targets Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a third Streamlit page that ranks fictional e-commerce merchants by deal opportunity score, helping analysts identify which merchants to prioritize for deal negotiations.

**Architecture:** A pure `compute_opportunity_score()` function in `utils/opportunity_score.py` does the math (no Streamlit dependency, fully unit-tested). A hardcoded CSV provides the 10 fictional merchant profiles. The page loads the CSV, applies the scoring function row-by-row, normalizes to 0–100, assigns priority tiers, and renders a ranked table plus two charts.

**Tech Stack:** Pandas, Altair, Streamlit, pytest

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `streamlit_app/data/ecommerce_merchants.csv` | Create | 10 fictional e-commerce merchant profiles |
| `streamlit_app/utils/opportunity_score.py` | Create | Pure scoring function — no Streamlit dependency |
| `tests/test_opportunity_score.py` | Create | 6 unit tests for the scoring function |
| `streamlit_app/pages/3_ecommerce_targets.py` | Create | Streamlit page: ranked table + two charts |
| `README.md` | Modify | Add `3_ecommerce_targets.py` to repo structure |

---

### Task 1: Create the merchant dataset

**Files:**
- Create: `streamlit_app/data/ecommerce_merchants.csv`

- [ ] **Step 1: Write the CSV**

Create `streamlit_app/data/ecommerce_merchants.csv` with exactly this content:

```csv
merchant_name,region,annual_volume_m,avg_transaction_usd,acceptance_rate,interchange_rate,yoy_growth_rate
NovaMart,North America,180.0,95.0,0.94,0.0241,0.12
Apex Digital,Europe,145.0,110.0,0.92,0.0238,0.18
TechDirect,Asia Pacific,120.0,75.0,0.89,0.0243,0.22
PacificCart,Asia Pacific,85.0,65.0,0.86,0.0240,0.15
SwiftBuy,North America,70.0,88.0,0.95,0.0237,0.08
GlobalBasket,Europe,55.0,105.0,0.91,0.0242,0.10
SkyShop,Middle East & Africa,40.0,80.0,0.84,0.0245,0.20
UrbanGoods,Latin America,35.0,60.0,0.83,0.0244,0.17
ClearMarket,North America,25.0,120.0,0.96,0.0236,0.06
NexusStore,Middle East & Africa,15.0,70.0,0.82,0.0246,0.14
```

- [ ] **Step 2: Verify the file**

Run:
```bash
python -c "import pandas as pd; df = pd.read_csv('streamlit_app/data/ecommerce_merchants.csv'); print(df.shape, df.columns.tolist())"
```
Expected output: `(10, 7) ['merchant_name', 'region', 'annual_volume_m', 'avg_transaction_usd', 'acceptance_rate', 'interchange_rate', 'yoy_growth_rate']`

- [ ] **Step 3: Commit**

```bash
git add streamlit_app/data/ecommerce_merchants.csv
git commit -m "data: add fictional e-commerce merchant profiles for targeting page"
```

---

### Task 2: Write and test the opportunity score function (TDD)

**Files:**
- Create: `streamlit_app/utils/opportunity_score.py`
- Create: `tests/test_opportunity_score.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_opportunity_score.py`:

```python
import pytest
from utils.opportunity_score import compute_opportunity_score


def test_zero_volume_returns_zero():
    score = compute_opportunity_score(
        annual_volume_m=0.0,
        avg_transaction_usd=100.0,
        interchange_rate=0.024,
        acceptance_rate=0.90,
        yoy_growth_rate=0.10,
    )
    assert score == pytest.approx(0.0)


def test_perfect_acceptance_sets_network_gap_to_one():
    # network_gap_multiplier = 2.0 - 1.0 = 1.0
    # score = volume * avg_txn * rate * (1 + growth) * 1.0
    score = compute_opportunity_score(
        annual_volume_m=10.0,
        avg_transaction_usd=100.0,
        interchange_rate=0.020,
        acceptance_rate=1.0,
        yoy_growth_rate=0.0,
    )
    assert score == pytest.approx(10.0 * 100.0 * 0.020 * 1.0 * 1.0)


def test_zero_growth_applies_no_growth_multiplier():
    # growth_multiplier = 1 + 0 = 1.0, so score = gross_revenue_m * network_gap
    score = compute_opportunity_score(
        annual_volume_m=10.0,
        avg_transaction_usd=100.0,
        interchange_rate=0.020,
        acceptance_rate=0.90,
        yoy_growth_rate=0.0,
    )
    expected = 10.0 * 100.0 * 0.020 * 1.0 * (2.0 - 0.90)
    assert score == pytest.approx(expected)


def test_higher_volume_produces_higher_score():
    base_kwargs = dict(avg_transaction_usd=100.0, interchange_rate=0.024,
                       acceptance_rate=0.90, yoy_growth_rate=0.10)
    low = compute_opportunity_score(annual_volume_m=50.0, **base_kwargs)
    high = compute_opportunity_score(annual_volume_m=100.0, **base_kwargs)
    assert high > low


def test_higher_growth_produces_higher_score():
    base_kwargs = dict(annual_volume_m=50.0, avg_transaction_usd=100.0,
                       interchange_rate=0.024, acceptance_rate=0.90)
    low = compute_opportunity_score(yoy_growth_rate=0.05, **base_kwargs)
    high = compute_opportunity_score(yoy_growth_rate=0.20, **base_kwargs)
    assert high > low


def test_lower_acceptance_rate_produces_higher_score():
    # Lower acceptance = more room to improve = higher network gap multiplier
    base_kwargs = dict(annual_volume_m=50.0, avg_transaction_usd=100.0,
                       interchange_rate=0.024, yoy_growth_rate=0.10)
    low_gap = compute_opportunity_score(acceptance_rate=0.95, **base_kwargs)
    high_gap = compute_opportunity_score(acceptance_rate=0.82, **base_kwargs)
    assert high_gap > low_gap
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_opportunity_score.py -v
```
Expected: 6 errors — `ModuleNotFoundError: No module named 'utils.opportunity_score'`

- [ ] **Step 3: Implement the function**

Create `streamlit_app/utils/opportunity_score.py`:

```python
def compute_opportunity_score(
    annual_volume_m: float,
    avg_transaction_usd: float,
    interchange_rate: float,
    acceptance_rate: float,
    yoy_growth_rate: float,
) -> float:
    """
    Score a merchant's deal opportunity.

    Formula:
        gross_revenue_m       = annual_volume_m * avg_transaction_usd * interchange_rate
        growth_multiplier     = 1 + yoy_growth_rate
        network_gap_multiplier = 2.0 - acceptance_rate  (lower acceptance = more upside)

        score = gross_revenue_m * growth_multiplier * network_gap_multiplier

    Args:
        annual_volume_m: Annual transaction volume in millions
        avg_transaction_usd: Average transaction value in USD
        interchange_rate: Interchange rate as a decimal (e.g. 0.024 = 2.4%)
        acceptance_rate: Share of transactions approved as a decimal (e.g. 0.90)
        yoy_growth_rate: Expected year-over-year volume growth as a decimal

    Returns:
        Raw opportunity score (higher = better deal candidate)
    """
    gross_revenue_m = annual_volume_m * avg_transaction_usd * interchange_rate
    growth_multiplier = 1 + yoy_growth_rate
    network_gap_multiplier = 2.0 - acceptance_rate
    return gross_revenue_m * growth_multiplier * network_gap_multiplier
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_opportunity_score.py -v
```
Expected: 6 passed

- [ ] **Step 5: Run full test suite to confirm no regressions**

```bash
pytest
```
Expected: 14 passed (8 existing + 6 new)

- [ ] **Step 6: Commit**

```bash
git add streamlit_app/utils/opportunity_score.py tests/test_opportunity_score.py
git commit -m "feat: add opportunity score pure function with 6 unit tests (TDD)"
```

---

### Task 3: Build the Streamlit page

**Files:**
- Create: `streamlit_app/pages/3_ecommerce_targets.py`

- [ ] **Step 1: Create the page**

Create `streamlit_app/pages/3_ecommerce_targets.py`:

```python
import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path
from utils.opportunity_score import compute_opportunity_score

st.set_page_config(page_title="E-commerce Targets", page_icon="🎯", layout="wide")

st.title("E-commerce Merchant Targets")
st.caption(
    "Merchants ranked by deal opportunity score — combines volume, "
    "growth trajectory, and network improvement potential."
)

# ── Load merchant data ────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "data" / "ecommerce_merchants.csv"

@st.cache_data
def load_merchants() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)

df = load_merchants()

# ── Compute opportunity scores ────────────────────────────────────────────────
df["raw_score"] = df.apply(
    lambda r: compute_opportunity_score(
        annual_volume_m=r["annual_volume_m"],
        avg_transaction_usd=r["avg_transaction_usd"],
        interchange_rate=r["interchange_rate"],
        acceptance_rate=r["acceptance_rate"],
        yoy_growth_rate=r["yoy_growth_rate"],
    ),
    axis=1,
)

# Normalize to 0–100
min_s, max_s = df["raw_score"].min(), df["raw_score"].max()
df["score"] = ((df["raw_score"] - min_s) / (max_s - min_s) * 100).round(1)

df = df.sort_values("score", ascending=False).reset_index(drop=True)

# Priority tiers
df["priority"] = pd.cut(
    df["score"],
    bins=[-1, 34.9, 64.9, 100],
    labels=["Low", "Medium", "High"],
)

# ── KPI cards ─────────────────────────────────────────────────────────────────
total_volume = df["annual_volume_m"].sum()
high_priority_count = (df["priority"] == "High").sum()

k1, k2, k3 = st.columns(3)
k1.metric("Total Addressable Volume", f"{total_volume:.0f}M txns/yr")
k2.metric("High-Priority Targets", f"{high_priority_count} merchants")
k3.metric("Avg Interchange Rate", f"{df['interchange_rate'].mean() * 100:.3f}%")

st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Opportunity Score by Merchant")
    bar = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("score:Q", title="Opportunity Score (0–100)"),
            y=alt.Y("merchant_name:N", sort="-x", title=""),
            color=alt.Color(
                "priority:N",
                scale=alt.Scale(
                    domain=["High", "Medium", "Low"],
                    range=["#2ecc71", "#f39c12", "#e74c3c"],
                ),
                title="Priority",
            ),
            tooltip=[
                alt.Tooltip("merchant_name:N", title="Merchant"),
                alt.Tooltip("score:Q", title="Score", format=".1f"),
                alt.Tooltip("priority:N", title="Priority"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(bar, use_container_width=True)

with col2:
    st.subheader("Volume vs Acceptance Rate")
    scatter = (
        alt.Chart(df)
        .mark_circle()
        .encode(
            x=alt.X("acceptance_rate:Q", title="Acceptance Rate",
                     axis=alt.Axis(format=".0%"), scale=alt.Scale(zero=False)),
            y=alt.Y("annual_volume_m:Q", title="Annual Volume (M txns)"),
            size=alt.Size("score:Q", title="Opportunity Score",
                          scale=alt.Scale(range=[100, 1200])),
            color=alt.Color(
                "priority:N",
                scale=alt.Scale(
                    domain=["High", "Medium", "Low"],
                    range=["#2ecc71", "#f39c12", "#e74c3c"],
                ),
                title="Priority",
            ),
            tooltip=[
                alt.Tooltip("merchant_name:N", title="Merchant"),
                alt.Tooltip("annual_volume_m:Q", title="Volume (M)", format=".0f"),
                alt.Tooltip("acceptance_rate:Q", title="Acceptance Rate", format=".1%"),
                alt.Tooltip("score:Q", title="Score", format=".1f"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(scatter, use_container_width=True)

# ── Ranked table ──────────────────────────────────────────────────────────────
st.subheader("Ranked Merchant Table")

display_df = pd.DataFrame({
    "Rank": range(1, len(df) + 1),
    "Merchant": df["merchant_name"].values,
    "Region": df["region"].values,
    "Volume (M txns/yr)": df["annual_volume_m"].map("{:.0f}".format).values,
    "Avg Transaction": df["avg_transaction_usd"].map("${:.0f}".format).values,
    "Acceptance Rate": df["acceptance_rate"].map("{:.1%}".format).values,
    "YoY Growth": df["yoy_growth_rate"].map("{:.0%}".format).values,
    "Interchange Rate": df["interchange_rate"].map("{:.3%}".format).values,
    "Score": df["score"].map("{:.1f}".format).values,
    "Priority": df["priority"].astype(str).values,
})

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.caption(
    "Opportunity Score = gross revenue potential × growth multiplier × network gap multiplier. "
    "Network gap = 2 − acceptance rate (lower acceptance = more upside from network improvements). "
    "Scores normalized 0–100 across this merchant set."
)
```

- [ ] **Step 2: Run the app locally and verify the page renders**

```bash
cd streamlit_app
streamlit run 1_market_overview.py
```

Check that:
- "E-commerce Targets" appears in the sidebar as page 3
- KPI cards show: ~670M txns/yr total, 3 high-priority merchants
- Bar chart shows NovaMart or Apex Digital at the top
- Scatter plot renders with varying bubble sizes
- Ranked table shows all 10 merchants sorted by Score descending

- [ ] **Step 3: Commit**

```bash
git add streamlit_app/pages/3_ecommerce_targets.py
git commit -m "feat: add e-commerce merchant targeting page with ranked opportunity scores"
```

---

### Task 4: Update README repo structure

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the repo structure block**

In `README.md`, find the repository structure section and update the pages listing from:

```
    │   ├── pages/
    │   │   └── 2_deal_simulator.py  # Page 2: Deal Simulator
```

to:

```
    │   ├── pages/
    │   │   ├── 2_deal_simulator.py       # Page 2: Deal Simulator
    │   │   └── 3_ecommerce_targets.py    # Page 3: E-commerce Merchant Targets
```

Also update the utils listing from:

```
    │   ├── utils/
    │   │   ├── data_loader.py       # Shared cached CSV loader
    │   │   └── deal_pnl.py          # Core financial model (pure function)
```

to:

```
    │   ├── utils/
    │   │   ├── data_loader.py            # Shared cached CSV loader
    │   │   ├── deal_pnl.py               # Core financial model (pure function)
    │   │   └── opportunity_score.py      # Merchant opportunity scoring (pure function)
```

Also update the data listing from:

```
    │   ├── data/
    │   │   └── visa_pricing_metrics.csv
```

to:

```
    │   ├── data/
    │   │   ├── visa_pricing_metrics.csv
    │   │   └── ecommerce_merchants.csv
```

- [ ] **Step 2: Commit and push**

```bash
git add README.md
git commit -m "docs: update repo structure for e-commerce targets page"
git push origin main
```
