import streamlit as st
st.set_page_config(page_title="Barzel Analytics — Dubai (V2)", layout="wide")

from src.app.ui import hero

hero(
    "Barzel Analytics — Dubai (V2)",
    "Analytical cockpit (no decision in UI). PDF memo contains the decision narrative.",
)

st.info("Use the left sidebar to navigate pages.")
