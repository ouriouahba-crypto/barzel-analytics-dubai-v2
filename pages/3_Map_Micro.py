import streamlit as st
import plotly.express as px

from src.app.ui import hero, apply_plotly_theme


hero("Geo Intelligence", "Micro-level spatial signals (descriptive only).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

need = ["latitude", "longitude"]
if not all(c in df.columns for c in need):
    st.error("Missing latitude / longitude columns.")
    st.stop()

view = df.dropna(subset=["latitude", "longitude"])

st.caption(f"Geolocated listings: {len(view):,}")

fig = px.scatter_mapbox(
    view,
    lat="latitude",
    lon="longitude",
    hover_data=[c for c in ["district", "price_per_sqm", "days_on_market"] if c in view.columns],
    zoom=11,
    height=520,
)

fig.update_layout(
    mapbox_style="carto-darkmatter",
    margin=dict(l=0, r=0, t=0, b=0),
)

st.plotly_chart(fig, use_container_width=True)
