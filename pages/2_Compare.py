import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme


hero("Compare", "District comparison across core descriptive metrics (no score).")

df = st.session_state.get("df")
if df is None or df.empty or "district" not in df.columns:
    st.stop()

# Support both column naming schemes
pps_col = "price_per_sqm" if "price_per_sqm" in df.columns else ("price_per_sqm_aed" if "price_per_sqm_aed" in df.columns else None)
dom_col = "days_on_market" if "days_on_market" in df.columns else ("days_active" if "days_active" in df.columns else None)

if not pps_col or not dom_col:
    st.error("Missing required columns for Compare. Need price_per_sqm (or price_per_sqm_aed) and days_on_market (or days_active).")
    st.stop()

g = df.groupby("district", dropna=True).agg(
    listings=("district", "size"),
    median_pps=(pps_col, "median"),
    iqr_pps=(pps_col, lambda s: s.quantile(0.75) - s.quantile(0.25)),
    median_dom=(dom_col, "median"),
).reset_index()

# Top “cards”
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Districts", f"{g['district'].nunique():,}", "Coverage")
with c2:
    kpi_card("Total listings", f"{int(g['listings'].sum()):,}", "Across selected dataset")
with c3:
    kpi_card("Best median AED/sqm", f"{int(g['median_pps'].min()):,}" if g["median_pps"].notna().any() else "n/a", "Cheapest district median")
with c4:
    kpi_card("Fastest median DOM", f"{int(g['median_dom'].min()):,}" if g["median_dom"].notna().any() else "n/a", "Shortest time-to-exit")

st.divider()

st.subheader("District table")
st.dataframe(g.sort_values("listings", ascending=False), use_container_width=True)

st.divider()

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(g.sort_values("median_pps"), x="district", y="median_pps", title="Median AED/sqm (by district)")
    fig.update_layout(xaxis_title="District", yaxis_title="Median AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

with c2:
    fig = px.bar(g.sort_values("median_dom"), x="district", y="median_dom", title="Median Days on Market (by district)")
    fig.update_layout(xaxis_title="District", yaxis_title="Median Days on Market")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

fig = px.bar(g.sort_values("iqr_pps"), x="district", y="iqr_pps", title="Dispersion proxy: IQR of AED/sqm (by district)")
fig.update_layout(xaxis_title="District", yaxis_title="IQR AED per sqm")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
