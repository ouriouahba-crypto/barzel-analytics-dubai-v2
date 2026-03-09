import streamlit as st
import plotly.express as px
import pandas as pd

from src.app.ui import (
    hero, kpi_card, selection_bar, apply_plotly_theme,
    section_intro, takeaway, metric_group_label
)
from src.analytics.kpi_engine import floor_weighted_price
from src.analytics.market_views import snapshots_by


hero("Map & Micro", "Geospatial market distribution and building-level competitive analysis.")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = selection_bar(districts, label="Districts", default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

# ===== MACRO LOCATION VIEW =====
st.markdown("")
section_intro("Macro Location View", "District-level aggregation and market positioning across geography.")

# Top KPIs
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Total Listings", f"{len(view):,}", "In selection")
with c2:
    kpi_card(
        "Geolocated",
        f"{view[['latitude','longitude']].dropna().shape[0]:,}"
        if "latitude" in view.columns and "longitude" in view.columns
        else "n/a",
        "Map coverage",
    )
with c3:
    kpi_card(
        "Price Data Completeness",
        f"{view['price_per_sqm'].notna().mean():.0%}" if "price_per_sqm" in view.columns else "n/a",
        "Key field filled",
    )
with c4:
    kpi_card(
        "Liquidity Data Completeness",
        f"{view['days_on_market'].notna().mean():.0%}" if "days_on_market" in view.columns else "n/a",
        "Key field filled",
    )

st.divider()

# ===== DISTRICT-LEVEL AGGREGATION =====
macro_data = snapshots_by(view, "district")
if not macro_data.empty:
    section_intro("District Aggregation Summary", "Market concentration and key metrics by district.")
    macro_sorted = macro_data.sort_values("n_obs", ascending=False)
    display_cols = {
        'n_obs': 'Listings',
        'median_price_sqm': 'Median Price (AED/sqm)',
        'median_dom': 'Median DOM (days)',
        'net_yield_median': 'Median Yield (%)',
        'price_consistency_cv': 'Price Variation (CV)',
    }
    display_table = macro_sorted[[col for col in display_cols.keys() if col in macro_sorted.columns]].copy()
    display_table.columns = [display_cols.get(col, col) for col in display_table.columns]
    
    for col in display_table.columns:
        if 'AED' in col or 'Price' in col:
            display_table[col] = display_table[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "n/a")
        elif '%' in col or 'Yield' in col:
            display_table[col] = display_table[col].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "n/a")
        elif 'CV' in col or 'Variation' in col:
            display_table[col] = display_table[col].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "n/a")
        elif 'DOM' in col:
            display_table[col] = display_table[col].apply(lambda x: f"{int(x)}" if pd.notna(x) else "n/a")
    
    st.dataframe(display_table, use_container_width=True)

st.divider()

# ===== GEOSPATIAL MAP (LIGHT BASEMAP) =====
section_intro("Geographic Market Distribution", "Spatial clustering and listing density visualization.")
need = ["latitude", "longitude"]
if not all(c in view.columns for c in need):
    st.error("Missing latitude and longitude columns for map visualization.")
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
    title="Market Geographic Distribution (Colored by AED/sqm)",
)
fig.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=55, b=0))
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

if "price_per_sqm" in geo.columns:
    takeaway(f"Geographic spread: {len(geo):,} geolocated listings. Clustering and density reveal submarkets within selected districts.")

st.divider()

# ===== MICRO MARKET VIEW =====
st.markdown("")
section_intro("Micro Market View", "Building and property-level competitive positioning.")

# Floor premium analysis (vertical market dynamics)
st.markdown("")
metric_group_label("Vertical Market Segmentation")
fp = floor_weighted_price(view)
if fp.empty:
    st.info("Floor premium analysis unavailable (insufficient floor data).")
else:
    fig = px.line(
        fp,
        x="floor_bucket",
        y="weighted_price_sqm",
        markers=True,
        title="Weighted Price Premium by Floor Band",
        line_shape="spline",
    )
    fig.update_layout(xaxis_title="Floor Band", yaxis_title="Weighted AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    if len(fp) > 1:
        max_floor = fp.loc[fp['weighted_price_sqm'].idxmax()]
        min_floor = fp.loc[fp['weighted_price_sqm'].idxmin()]
        premium_pct = ((max_floor['weighted_price_sqm'] - min_floor['weighted_price_sqm']) / min_floor['weighted_price_sqm'] * 100)
        takeaway(f"Floor premium spans {premium_pct:.1f}%, indicating {'strong' if premium_pct > 15 else 'moderate'} vertical market stratification.")

st.divider()

# Building-level micro table
st.markdown("")
metric_group_label("Top Buildings Micro-Analysis")
if "building_name" in view.columns and "price_per_sqm" in view.columns:
    # Build aggregation dictionary based on available columns
    agg_specs = {"price_per_sqm": "median"}
    if "days_on_market" in view.columns:
        agg_specs["days_on_market"] = "median"
    
    # Group and aggregate
    building_stats = view.groupby("building_name", dropna=True).agg(agg_specs).reset_index()
    
    # Add listing count
    counts = view.groupby("building_name", dropna=True).size().reset_index(name="Listings")
    building_stats = building_stats.merge(counts, on="building_name")
    
    # Rename columns
    rename_map = {"price_per_sqm": "Median_Price"}
    if "days_on_market" in building_stats.columns:
        rename_map["days_on_market"] = "Median_DOM"
    
    building_stats = building_stats.rename(columns=rename_map)
    
    # Sort and limit
    building_stats = building_stats.sort_values("Listings", ascending=False).head(25)
    
    # Format display table
    display_building = building_stats.copy()
    display_cols = ["building_name", "Listings", "Median_Price"]
    if "Median_DOM" in display_building.columns:
        display_cols.append("Median_DOM")
    
    display_building = display_building[display_cols]
    display_building.columns = ["Building", "Listings", "Median Price (AED/sqm)"] + (["Median DOM (days)"] if "Median_DOM" in building_stats.columns else [])
    
    for col in display_building.columns:
        if "Price" in col:
            display_building[col] = display_building[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "n/a")
        elif "DOM" in col:
            display_building[col] = display_building[col].apply(lambda x: f"{int(x)}" if pd.notna(x) else "n/a")
        elif "Listings" in col:
            display_building[col] = display_building[col].apply(lambda x: f"{int(x)}" if pd.notna(x) else "n/a")
    
    st.dataframe(display_building, use_container_width=True)
    
    takeaway(f"Top building shows strong position: {building_stats.iloc[0]['Listings']} listings, market median AED/sqm: {building_stats['Median_Price'].median():.0f}.")
elif "building_name" in view.columns:
    b = view.groupby("building_name", dropna=True).size().reset_index(name="Listings")
    b = b.sort_values("Listings", ascending=False).head(20)
    st.dataframe(b, use_container_width=True)
else:
    st.info("Building-level data not available.")
