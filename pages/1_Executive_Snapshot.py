import streamlit as st
import numpy as np
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme


hero("Executive Snapshot", "High-level descriptive cockpit (no decision, no score).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

st.caption("All metrics are descriptive. No ranking or recommendation in the UI.")

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

# Columns (support both possible names)
pps_col = "price_per_sqm" if "price_per_sqm" in view.columns else ("price_per_sqm_aed" if "price_per_sqm_aed" in view.columns else None)
dom_col = "days_on_market" if "days_on_market" in view.columns else ("days_active" if "days_active" in view.columns else None)

pps = view[pps_col].dropna().astype(float) if pps_col else np.array([])
dom = view[dom_col].dropna().astype(float) if dom_col else np.array([])

# KPI cards row
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Listings", f"{len(view):,}", "Sample size")
with c2:
    kpi_card("Median AED/sqm", f"{int(np.median(pps)):,}" if len(pps) else "n/a", "Pricing level")
with c3:
    kpi_card("IQR AED/sqm", f"{int(np.percentile(pps,75)-np.percentile(pps,25)):,}" if len(pps) else "n/a", "Dispersion proxy")
with c4:
    kpi_card("Median DOM", f"{int(np.median(dom)):,}" if len(dom) else "n/a", "Exit speed")

st.divider()

# Coverage cards
st.subheader("Coverage")
cc1, cc2 = st.columns(2)
with cc1:
    if pps_col:
        kpi_card("Price/sqm coverage", f"{view[pps_col].notna().mean():.0%}", "Share of listings with price/sqm")
    else:
        kpi_card("Price/sqm coverage", "n/a", "Missing column")
with cc2:
    if dom_col:
        kpi_card("DOM coverage", f"{view[dom_col].notna().mean():.0%}", "Share of listings with DOM")
    else:
        kpi_card("DOM coverage", "n/a", "Missing column")

st.divider()

# Simple “fintech” charts
left, right = st.columns(2)

with left:
    if pps_col and len(pps) >= 30:
        fig = px.histogram(view.dropna(subset=[pps_col]), x=pps_col, nbins=40, title="Distribution: AED/sqm")
        fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Count")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
    else:
        st.info("Not enough data for AED/sqm distribution.")

with right:
    if dom_col and len(dom) >= 30:
        fig = px.histogram(view.dropna(subset=[dom_col]), x=dom_col, nbins=40, title="Distribution: Days on Market")
        fig.update_layout(xaxis_title="Days on Market", yaxis_title="Count")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
    else:
        st.info("Not enough data for DOM distribution.")
