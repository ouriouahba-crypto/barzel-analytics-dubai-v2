import streamlit as st
st.set_page_config(page_title="Barzel Analytics — Dubai (V2)", layout="wide")

from src.app.ui import hero, load_data
from src.processing.assemble import assemble


# Load once + normalize facts
if "df" not in st.session_state:
    st.session_state["df"] = assemble(load_data())

df = st.session_state["df"]

hero(
    "Barzel Analytics — Dubai (V2)",
    "Analytical cockpit (no decision in UI). PDF memo contains the decision narrative.",
)

with st.expander("Data status", expanded=False):
    st.write(f"Rows: **{len(df):,}**")
    st.write(f"Columns: **{len(df.columns):,}**")
    if "district" in df.columns:
        st.write("Districts:", sorted([d for d in df["district"].dropna().unique()]))

st.info("Use the left sidebar to navigate pages.")
