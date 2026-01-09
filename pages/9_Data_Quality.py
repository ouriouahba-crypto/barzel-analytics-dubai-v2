import streamlit as st
import pandas as pd
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme


hero("Data", "Coverage, completeness, freshness (descriptive only).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

# Cards
c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Rows", f"{len(df):,}", "Dataset size")
with c2: kpi_card("Columns", f"{len(df.columns):,}", "Schema width")

if "first_seen" in df.columns and "last_seen" in df.columns:
    fs = pd.to_datetime(df["first_seen"], errors="coerce", utc=True)
    ls = pd.to_datetime(df["last_seen"], errors="coerce", utc=True)
    with c3: kpi_card("First seen (min)", fs.min().date().isoformat() if fs.notna().any() else "n/a", "Coverage start")
    with c4: kpi_card("Last seen (max)", ls.max().date().isoformat() if ls.notna().any() else "n/a", "Coverage end")
else:
    with c3: kpi_card("First seen", "n/a", "Missing column")
    with c4: kpi_card("Last seen", "n/a", "Missing column")

st.divider()

# Coverage table
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
st.subheader("Column coverage")
st.dataframe(summary, use_container_width=True)

st.divider()

# Coverage chart
fig = px.bar(summary.tail(25), x="coverage_pct", y="column", orientation="h", title="Top 25 columns by coverage (%)")
fig.update_layout(xaxis_title="Coverage (%)", yaxis_title="Column")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

# Missingness by district
if "district" in df.columns:
    st.divider()
    st.subheader("Coverage by district (core fields)")
    core = [c for c in ["price_per_sqm", "days_on_market", "net_yield", "service_charge_psm_year", "latitude", "longitude"] if c in df.columns]
    if core:
        rows = []
        for dname, sub in df.groupby("district", dropna=True):
            row = {"district": dname, "n": len(sub)}
            for c in core:
                row[c] = float(sub[c].notna().mean())
            rows.append(row)
        out = pd.DataFrame(rows).sort_values("n", ascending=False)
        st.dataframe(out, use_container_width=True)
