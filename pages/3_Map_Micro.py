import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, selection_bar, apply_plotly_theme
from src.analytics.kpi_engine import floor_weighted_price


hero("Map & Micro", "Geospatial and micro-level market insights.")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = selection_bar(districts, label="Districts", default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

# Top cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Listings", f"{len(view):,}", "In selection")
with c2:
    kpi_card(
        "Geo Coverage",
        f"{view[['latitude','longitude']].dropna().shape[0]:,}"
        if "latitude" in view.columns and "longitude" in view.columns
        else "n/a",
        "Geolocated",
    )
with c3:
    kpi_card(
        "Price Data",
        f"{view['price_per_sqm'].notna().mean():.0%}" if "price_per_sqm" in view.columns else "n/a",
        "Completeness",
    )
with c4:
    kpi_card(
        "Time Data",
        f"{view['days_on_market'].notna().mean():.0%}" if "days_on_market" in view.columns else "n/a",
        "Completeness",
    )

st.markdown("")

# Map
need = ["latitude", "longitude"]
if not all(c in view.columns for c in need):
    st.error("Missing latitude and longitude columns.")
    st.stop()

geo = view.dropna(subset=["latitude", "longitude"]).copy()
if geo.empty:
    st.info("No geolocated listings in selection.")
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
    title="Market Map (colored by AED/sqm)",
)
fig.update_layout(mapbox_style="carto-darkmatter", margin=dict(l=0, r=0, t=55, b=0))
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown("")

# Floor premium (weighted)
st.subheader("Floor Premium Analysis")
fp = floor_weighted_price(view)
if fp.empty:
    st.info("Insufficient data for floor premium analysis.")
else:
    fig = px.line(
        fp,
        x="floor_bucket",
        y="weighted_price_sqm",
        markers=True,
        title="Price Curve by Floor",
    )
    fig.update_layout(xaxis_title="Floor range", yaxis_title="Weighted AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

st.markdown("")

# Building-level micro table
if "building_name" in view.columns:
    st.subheader("Top Buildings")
    b = view.groupby("building_name", dropna=True).size().reset_index(name="Listings")
    b = b.sort_values("Listings", ascending=False).head(20)
    st.dataframe(b, use_container_width=True)
