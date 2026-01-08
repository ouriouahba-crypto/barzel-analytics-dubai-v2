import streamlit as st
import plotly.express as px
from src.app.ui import load_data, hero
from src.processing.assemble import assemble

hero("Compare", "Compare districts across core descriptive metrics.")

df = assemble(load_data())
if df.empty or "district" not in df.columns:
    st.stop()

g = df.groupby("district", dropna=True).agg(
    listings=("district", "size"),
    median_pps=("price_per_sqm", "median"),
    iqr_pps=("price_per_sqm", lambda s: s.quantile(0.75) - s.quantile(0.25)),
    median_dom=("days_active", "median"),
).reset_index()

st.dataframe(g, use_container_width=True)

st.divider()
c1, c2 = st.columns(2)

with c1:
    fig = px.bar(g, x="district", y="median_pps", title="Median AED/sqm (by district)")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.bar(g, x="district", y="median_dom", title="Median Days Active (by district)")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
fig = px.bar(g, x="district", y="iqr_pps", title="Dispersion proxy: IQR of AED/sqm (by district)")
st.plotly_chart(fig, use_container_width=True)
