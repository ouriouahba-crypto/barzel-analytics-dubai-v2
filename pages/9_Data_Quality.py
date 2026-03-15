import streamlit as st
import pandas as pd
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme, section_intro, chart_explanation
from src.app.translations import get_text

lang = st.session_state.get("language", "en")

hero(get_text("data_title", lang), get_text("data_subtitle", lang))

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

# Cards
c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card(get_text("kpi_rows", lang), f"{len(df):,}", get_text("dataset_size", lang))
with c2: kpi_card(get_text("kpi_columns", lang), f"{len(df.columns):,}", get_text("schema_width", lang))

if "first_seen" in df.columns and "last_seen" in df.columns:
    fs = pd.to_datetime(df["first_seen"], errors="coerce", utc=True)
    ls = pd.to_datetime(df["last_seen"], errors="coerce", utc=True)
    with c3: kpi_card(get_text("kpi_first_seen", lang), fs.min().date().isoformat() if fs.notna().any() else "n/a", get_text("coverage_start", lang))
    with c4: kpi_card(get_text("kpi_last_seen", lang), ls.max().date().isoformat() if ls.notna().any() else "n/a", get_text("coverage_end", lang))
else:
    with c3: kpi_card(get_text("kpi_first_seen_missing", lang), "n/a", get_text("column_missing", lang))
    with c4: kpi_card(get_text("kpi_last_seen_missing", lang), "n/a", get_text("column_missing", lang))

st.divider()

# Coverage table
section_intro(get_text("section_column_coverage", lang), get_text("coverage_table_sub", lang))
chart_explanation(get_text("coverage_explanation", lang))
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

st.divider()

# Coverage chart
section_intro(get_text("section_coverage_viz", lang), get_text("coverage_viz_sub", lang))
chart_explanation(get_text("completeness_explanation", lang))
fig = px.bar(summary.tail(25), x="coverage_pct", y="column", orientation="h", title=get_text("chart_top_columns", lang))
fig.update_layout(xaxis_title="Coverage (%)", yaxis_title="Column")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

# Missingness by district
if "district" in df.columns:
    st.divider()
    section_intro(get_text("section_coverage_district", lang), get_text("district_coverage_sub", lang))
    chart_explanation(get_text("district_explanation", lang))
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
