import streamlit as st
import plotly.express as px

from src.app.ui import hero, apply_plotly_theme


hero("Pricing Engine", "Pricing structure & dispersion analysis.")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

col = "price_per_sqm" if "price_per_sqm" in df.columns else "price_per_sqm_aed"
if col not in df.columns:
    st.error("Missing price per sqm column.")
    st.stop()

view = df.dropna(subset=[col])

fig = px.box(
    view,
    x="district",
    y=col,
    title="Price per sqm dispersion by district",
)

fig.update_layout(xaxis_title="District", yaxis_title="AED per sqm")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
