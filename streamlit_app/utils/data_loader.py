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
