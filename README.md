# Visa NA VAS — Sales Enablement AI Solutions Analyst

This project models the analytical and AI automation work performed by a Sales Enablement
AI Solutions Analyst on Visa's North America Visa Acceptance Solutions (NA VAS) team.
It synthesises two datasets — 288 rows of monthly pipeline data across 4 VAS products
and 4 acquirer segments, and 200 individual deal snapshots — to demonstrate pipeline
health tracking, velocity analysis, post-sale time-to-revenue monitoring, and an
automated AI deal recommendation engine.

## Live Dashboard

**URL:** https://sales-analyst-hpecckbmvzzbhe6a5owuax.streamlit.app/

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
| Testing | pytest (15 unit tests) |
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
    │   ├── test_deal_health.py            # 8 unit tests
    │   └── test_ai_recommendations.py     # 7 unit tests
    ├── pytest.ini
    └── README.md
