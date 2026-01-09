import streamlit as st
import plotly.express as px

from src.app.ui import hero, apply_plotly_theme


hero("Costs & Friction", "Service charges and cost pressure.")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

col = "service_charge_psm_year" if "service_charge_psm_year" in df.columns else "service_charge_aed_per_sqm_year"
if col not in df.columns:
    st.error("Missing service charge column.")
    st.stop()

view = df.dropna(subset=[col])

fig = px.histogram(
    view,
    x=col,
    nbins=30,
    title="Service charges distribution (AED / sqm / year)",
)

fig.update_layout(xaxis_title="AED / sqm / year", yaxis_title="Listings")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
