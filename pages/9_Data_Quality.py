import streamlit as st

from src.app.ui import hero
from src.analytics.aggregations import coverage_table


hero("Data Quality", "Coverage, sample sizes, and reliability warnings (no score).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

st.subheader("Core coverage table")

core_cols = [
    "district",
    "building_name",
    "bedrooms",
    "size_sqm",
    "floor",
    "price_per_sqm",
    "days_on_market",
    "gross_yield",
    "net_yield",
    "vacancy_days",
    "service_charge_psm_year",
    "has_terrace",
    "terrace_size_sqm",
    "latitude",
    "longitude",
    "first_seen",
    "last_seen",
]

t = coverage_table(df, core_cols)
st.dataframe(t, use_container_width=True)

st.divider()

st.subheader("Sample size by district")
if "district" in df.columns:
    s = df["district"].value_counts().reset_index()
    s.columns = ["district", "n"]
    st.dataframe(s, use_container_width=True)

st.divider()

st.subheader("Warnings (hard rules)")
warnings = []
# min sample alerts
if "district" in df.columns:
    vc = df["district"].value_counts()
    small = vc[vc < 50]
    if len(small):
        warnings.append(f"Some districts have low sample size (<50): {', '.join(small.index.astype(str).tolist())}")
# terrace coverage
if "has_terrace" in df.columns:
    cov = float(df["has_terrace"].notna().mean())
    if cov < 0.3:
        warnings.append(f"Terrace coverage is low ({cov:.0%}). Treat terrace analytics with caution.")
# lat/long coverage
if "latitude" in df.columns and "longitude" in df.columns:
    cov_geo = float(df["latitude"].notna().mean() * df["longitude"].notna().mean())
    if cov_geo < 0.5:
        warnings.append("Geo coverage is limited. Map micro may be incomplete.")

if warnings:
    for w in warnings:
        st.warning(w)
else:
    st.success("No critical warnings triggered.")
