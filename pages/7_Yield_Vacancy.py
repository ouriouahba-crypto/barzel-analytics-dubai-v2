import streamlit as st
import plotly.express as px

from src.app.ui import hero, apply_plotly_theme


hero("Income & Vacancy", "Yield structure and income efficiency.")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

if "net_yield" not in df.columns:
    st.error("Missing net_yield column.")
    st.stop()

view = df.dropna(subset=["net_yield"])

fig = px.histogram(
    view,
    x="net_yield",
    nbins=30,
    title="Net yield distribution",
)

fig.update_layout(xaxis_title="Net yield (%)", yaxis_title="Listings")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
