import streamlit as st
import numpy as np
from src.app.ui import load_data, hero
from src.processing.assemble import assemble

hero("Executive Snapshot", "High-level descriptive metrics (no decision).")

df = assemble(load_data())
if df.empty:
    st.stop()

st.caption("All metrics are descriptive. No ranking or recommendation in the UI.")

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)

view = df[df["district"].isin(sel)] if sel else df

c1, c2, c3, c4 = st.columns(4)
c1.metric("Listings", f"{len(view):,}")
pps = view["price_per_sqm"].dropna() if "price_per_sqm" in view.columns else []
dom = view["days_active"].dropna() if "days_active" in view.columns else []

c2.metric("Median AED/sqm", f"{int(np.median(pps)):,}" if len(pps) else "n/a")
c3.metric("IQR AED/sqm", f"{int(np.percentile(pps,75)-np.percentile(pps,25)):,}" if len(pps) else "n/a")
c4.metric("Median Days Active", f"{int(np.median(dom)):,}" if len(dom) else "n/a")

st.divider()
st.subheader("Coverage")
cov1, cov2 = st.columns(2)
cov1.metric("Price/sqm coverage", f"{view['price_per_sqm'].notna().mean():.0%}" if "price_per_sqm" in view.columns else "n/a")
cov2.metric("Days active coverage", f"{view['days_active'].notna().mean():.0%}" if "days_active" in view.columns else "n/a")
