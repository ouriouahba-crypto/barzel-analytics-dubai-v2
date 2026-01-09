import streamlit as st
import plotly.express as px

from src.app.ui import hero, apply_plotly_theme


hero("Liquidity & Exit", "Time-to-exit and pricing discipline.")

df = st.session_state.get("df")
if df is None or df.empty or "days_on_market" not in df.columns:
    st.stop()

view = df.dropna(subset=["days_on_market"])

fig = px.histogram(
    view,
    x="days_on_market",
    nbins=40,
    title="Distribution of days on market",
)

fig.update_layout(xaxis_title="Days on Market", yaxis_title="Listings")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
