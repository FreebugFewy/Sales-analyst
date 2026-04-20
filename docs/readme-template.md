# [Your project name]

[One paragraph: what business problem does this project address, what data sources does it use, and what insights does it deliver? 3-5 sentences.]

## Job Posting

- **Role:** [Job title]
- **Company:** [Company name]
- **Link:** [URL to posting]

[1-2 sentences on how your project demonstrates the skills this role requires.]

## Tech Stack

| Layer | Tool |
|---|---|
| Source 1 | [API name and type] |
| Source 2 | [Web scrape / document source] |
| Data Warehouse | Snowflake |
| Transformation | dbt |
| Orchestration | GitHub Actions |
| Dashboard | Streamlit |
| Knowledge Base | Claude Code (scrape → summarize → query) |

## Pipeline Diagram

[Insert your pipeline diagram here (image or Mermaid). Show all layers: sources, raw, staging, mart, dashboard, knowledge base. Label every tool.]

## ERD (Star Schema)

[Insert your ERD here (image or Mermaid). Show fact and dimension tables with relationships.]

## Dashboard Preview

[Insert a screenshot of your dashboard here.]

## Key Insights

**Descriptive (what happened?):** [Summarize your main finding with a Takeaway Title.]

**Diagnostic (why did it happen?):** [Summarize your root cause analysis.]

**Recommendation:** [Action] → [Expected outcome]

## Live Dashboard

**URL:** [Streamlit Community Cloud URL]

## Knowledge Base

A Claude Code-curated wiki built from [N] scraped sources. Wiki pages live in `knowledge/wiki/`, raw sources in `knowledge/raw/`. Browse `knowledge/index.md` to see all pages.

**Query it:** Open Claude Code in this repo and ask questions like:

- [Example question 1 your knowledge base can answer]
- [Example question 2]
- [Example question 3]

Claude Code reads the wiki pages first and falls back to raw sources when needed. See `CLAUDE.md` for the query conventions.

## Setup & Reproduction

[List what someone needs to run your pipeline (Python version, Snowflake account, etc.), then provide step-by-step instructions to reproduce.]

Copy `.env.example` to `.env` and fill in your credentials:

    SNOWFLAKE_ACCOUNT=
    SNOWFLAKE_USER=
    SNOWFLAKE_PASSWORD=
    SNOWFLAKE_DATABASE=
    SNOWFLAKE_SCHEMA=
    SNOWFLAKE_WAREHOUSE=
    # Add any additional variables your sources require

## Repository Structure

[Update this tree to match your actual project structure.]

    .
    ├── .github/workflows/    # GitHub Actions pipeline
    ├── extract/              # Extraction scripts
    ├── dbt_project/          # dbt models and tests
    ├── streamlit_app/        # Dashboard
    ├── knowledge/            # Knowledge base (raw sources + wiki pages)
    ├── docs/                 # Proposal, job posting, pipeline diagram, ERD, slides
    ├── .env.example          # Required environment variables
    ├── .gitignore
    ├── CLAUDE.md             # Project context for Claude Code
    └── README.md             # This file
