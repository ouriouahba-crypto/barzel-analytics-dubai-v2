import streamlit as st
from src.app.ui import load_data, hero
from src.processing.assemble import assemble

hero("Map & Micro", "Spatial exploration (descriptive).")

df = assemble(load_data())
needed = {"latitude", "longitude", "price_per_sqm"}
if df.empty or not needed.issubset(set(df.columns)):
    st.warning("Map requires latitude/longitude/price_per_sqm columns.")
    st.stop()

m = df.dropna(subset=["latitude", "longitude"])
st.map(m, use_container_width=True)
