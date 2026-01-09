import streamlit as st
import plotly.express as px

from src.app.ui import hero
from src.analytics.market_views import snapshots_by


hero("Map & Micro", "Spatial exploration + building analytics (no score).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

needed = {"latitude", "longitude", "price_per_sqm"}
if not needed.issubset(set(df.columns)):
    st.warning("Map requires latitude/longitude/price_per_sqm columns.")
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = st.selectbox("District", ["(All)"] + districts, index=0)
view = df[df["district"] == sel] if sel != "(All)" else df

m = view.dropna(subset=["latitude", "longitude", "price_per_sqm"]).copy()
st.map(m, use_container_width=True)

st.divider()

st.subheader("Building table (descriptive)")
if "building_name" not in view.columns:
    st.info("No building_name column.")
    st.stop()

b = snapshots_by(view.dropna(subset=["building_name"]), "building_name")
if b.empty:
    st.info("Not enough data.")
    st.stop()

b = b.sort_values("n_obs", ascending=False)

top_n = st.slider("Show top buildings (by sample size)", 10, 200, 50, step=10)
st.dataframe(b.head(top_n), use_container_width=True)

st.divider()

st.subheader("Micro charts (top buildings)")
pick = st.selectbox("Pick a building", b.head(200)["building_name"].tolist())
sub = view[view["building_name"] == pick]

c1, c2, c3 = st.columns(3)
c1.metric("Listings", f"{len(sub):,}")
c2.metric("Median AED/sqm", f"{int(sub['price_per_sqm'].median()):,}" if sub["price_per_sqm"].notna().any() else "n/a")
c3.metric("Median DOM", f"{int(sub['days_on_market'].median()):,}" if sub["days_on_market"].notna().any() else "n/a")

left, right = st.columns(2)
with left:
    fig = px.histogram(sub.dropna(subset=["price_per_sqm"]), x="price_per_sqm", nbins=30, title="AED/sqm distribution")
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.histogram(sub.dropna(subset=["days_on_market"]), x="days_on_market", nbins=30, title="Days on Market distribution")
    st.plotly_chart(fig, use_container_width=True)
