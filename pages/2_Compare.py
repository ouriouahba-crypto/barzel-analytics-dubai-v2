import streamlit as st
import plotly.express as px

from src.app.ui import hero
from src.analytics.market_views import snapshots_by


hero("Compare", "Compare districts with a multi-KPI cockpit (no score).")

df = st.session_state.get("df")
if df is None or df.empty or "district" not in df.columns:
    st.stop()

g = snapshots_by(df, "district")
if g.empty:
    st.stop()

st.dataframe(g.sort_values("n_obs", ascending=False), use_container_width=True)

st.divider()

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(g, x="district", y="median_price_sqm", title="Median AED/sqm by district")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.bar(g, x="district", y="median_dom", title="Median Days on Market by district")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

c3, c4 = st.columns(2)
with c3:
    fig = px.bar(g, x="district", y="net_yield_median", title="Net Yield (median) by district")
    st.plotly_chart(fig, use_container_width=True)

with c4:
    fig = px.bar(g, x="district", y="service_charge_median", title="Service charge (median) by district")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

fig = px.bar(g, x="district", y="overpricing_penalty_corr", title="Overpricing penalty (corr price vs DOM)")
st.plotly_chart(fig, use_container_width=True)
