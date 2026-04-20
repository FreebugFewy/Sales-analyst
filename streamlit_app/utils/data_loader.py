import pandas as pd
import streamlit as st
from pathlib import Path


@st.cache_data
def load_data() -> pd.DataFrame:
    path = Path(__file__).parent.parent / "data" / "crypto_programs.csv"
    df = pd.read_csv(path, parse_dates=["month"])
    return df
