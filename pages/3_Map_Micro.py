import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme
from src.analytics.kpi_engine import floor_weighted_price


hero("Map & Micro", "Micro-level exploration (descriptive only).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

# Top cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Listings", f"{len(view):,}", "Selection size")
with c2:
    kpi_card(
        "Geo coverage",
        f"{view[['latitude','longitude']].dropna().shape[0]:,}"
        if "latitude" in view.columns and "longitude" in view.columns
        else "n/a",
        "With lat/lon",
    )
with c3:
    kpi_card(
        "Price/sqm coverage",
        f"{view['price_per_sqm'].notna().mean():.0%}" if "price_per_sqm" in view.columns else "n/a",
        "Non-null share",
    )
with c4:
    kpi_card(
        "DOM coverage",
        f"{view['days_on_market'].notna().mean():.0%}" if "days_on_market" in view.columns else "n/a",
        "Non-null share",
    )

st.divider()

# Map
need = ["latitude", "longitude"]
if not all(c in view.columns for c in need):
    st.error("Missing latitude / longitude columns.")
    st.stop()

geo = view.dropna(subset=["latitude", "longitude"]).copy()
if geo.empty:
    st.info("No geolocated rows available.")
    st.stop()

color_col = "price_per_sqm" if "price_per_sqm" in geo.columns else None
hover_cols = [c for c in ["district", "building_name", "bedrooms", "size_sqm", "price_per_sqm", "days_on_market"] if c in geo.columns]

fig = px.scatter_mapbox(
    geo,
    lat="latitude",
    lon="longitude",
    color=color_col if color_col in geo.columns else None,
    hover_data=hover_cols,
    zoom=11,
    height=560,
    title="Geolocated listings (colored by AED/sqm when available)",
)
fig.update_layout(mapbox_style="carto-darkmatter", margin=dict(l=0, r=0, t=55, b=0))
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Floor premium (weighted)
st.subheader("Floor premium (weighted by sqm)")
fp = floor_weighted_price(view)
if fp.empty:
    st.info("Not enough data for floor premium.")
else:
    # NOTE: floor_weighted_price now returns floor_bucket instead of floor
    fig = px.line(
        fp,
        x="floor_bucket",
        y="weighted_price_sqm",
        markers=True,
        title="Weighted AED/sqm by floor range",
    )
    fig.update_layout(xaxis_title="Floor range", yaxis_title="Weighted AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

# Building-level micro table
if "building_name" in view.columns:
    st.subheader("Micro: Top buildings by listing count")
    b = view.groupby("building_name", dropna=True).size().reset_index(name="n_listings")
    b = b.sort_values("n_listings", ascending=False).head(20)
    st.dataframe(b, use_container_width=True)
