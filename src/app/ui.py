import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    path = Path("data/listings_enriched.csv")
    if not path.exists():
        st.error(f"Missing dataset: {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)

    # Minimal normalization (safe)
    if "district" in df.columns:
        df["district"] = df["district"].astype(str)

    for c in ["price", "size_sqm", "latitude", "longitude"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    for c in ["first_seen", "last_seen"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", utc=True)

    return df

def hero(title: str, subtitle: str):
    st.markdown(
        f"""
        <div style="padding: 0.8rem 0 0.2rem 0;">
          <h1 style="margin:0;">{title}</h1>
          <p style="color:#6b7280;margin:0.2rem 0 0 0;font-size:1.05rem;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
