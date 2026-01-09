import streamlit as st
import pandas as pd

from src.app.ui import hero


hero("Data Quality", "Coverage, completeness and reliability checks.")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

summary = (
    df.notna()
    .mean()
    .mul(100)
    .round(1)
    .rename("coverage_pct")
    .reset_index()
    .rename(columns={"index": "column"})
    .sort_values("coverage_pct")
)

st.dataframe(summary, use_container_width=True)
