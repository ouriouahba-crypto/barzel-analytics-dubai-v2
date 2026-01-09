import streamlit as st
import plotly.express as px

from src.app.ui import hero
from src.analytics.aggregations import group_stats, bucketize


hero("Pricing Lab", "Everything about pricing: AED/sqm, typology, floors, size-weighted views.")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

# Filters
districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel_d = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)

view = df[df["district"].isin(sel_d)] if sel_d else df

# Bedroom filter
if "bedrooms" in view.columns:
    beds = sorted(view["bedrooms"].dropna().unique().tolist())
    sel_b = st.multiselect("Bedrooms", beds, default=beds)
    if sel_b:
        view = view[view["bedrooms"].isin(sel_b)]

st.divider()

# 1) Price per sqm by bedrooms (quartiles)
st.subheader("Price per sqm by bedrooms (quantiles)")
if "bedrooms" in view.columns:
    t = group_stats(view, ["district", "bedrooms"], "price_per_sqm", weight_col="size_sqm", min_n=10)
    if t.empty:
        st.info("Not enough data.")
    else:
        st.dataframe(t, use_container_width=True)
        fig = px.line(
            t.sort_values(["district","bedrooms"]),
            x="bedrooms",
            y="q50",
            color="district",
            markers=True,
            title="Median AED/sqm by bedrooms (district lines)"
        )
        fig.update_layout(xaxis_title="Bedrooms", yaxis_title="Median AED/sqm")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No bedrooms column available.")

st.divider()

# 2) Floor premium heatmap (bucketed floors)
st.subheader("Floor premium (bucketed) — weighted by sqm")
if "floor" in view.columns:
    # Define floor buckets
    fb = bucketize(view["floor"], bins=[-1, 3, 10, 20, 40, 100], labels=["0-3","4-10","11-20","21-40","40+"])
    tmp = view.copy()
    tmp["floor_bucket"] = fb
    ht = group_stats(tmp, ["district", "floor_bucket"], "price_per_sqm", weight_col="size_sqm", min_n=10)
    if ht.empty:
        st.info("Not enough floor data.")
    else:
        pivot = ht.pivot(index="district", columns="floor_bucket", values="wmean" if "wmean" in ht.columns else "q50")
        pivot = pivot.reset_index().melt(id_vars=["district"], var_name="floor_bucket", value_name="aed_sqm")
        fig = px.density_heatmap(pivot, x="floor_bucket", y="district", z="aed_sqm", title="AED/sqm by district x floor bucket")
        fig.update_layout(xaxis_title="Floor bucket", yaxis_title="District")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No floor column.")

st.divider()

# 3) Size vs price (pricing curve)
st.subheader("Size vs price per sqm")
d = view.dropna(subset=["size_sqm","price_per_sqm"]).copy()
if len(d) < 30:
    st.info("Not enough data.")
else:
    fig = px.scatter(
        d,
        x="size_sqm",
        y="price_per_sqm",
        color="district" if "district" in d.columns else None,
        opacity=0.45,
        hover_data=[c for c in ["bedrooms","building_name","floor"] if c in d.columns],
        title="Scatter: size_sqm vs AED/sqm"
    )
    fig.update_layout(xaxis_title="Size (sqm)", yaxis_title="AED/sqm")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# 4) Building pricing ranking
st.subheader("Top buildings by median AED/sqm (min sample)")
if "building_name" in view.columns:
    min_n = st.slider("Min listings per building", 5, 50, 15, step=5)
    tb = group_stats(view, ["district","building_name"], "price_per_sqm", weight_col="size_sqm", min_n=min_n)
    if tb.empty:
        st.info("Not enough building data.")
    else:
        tb = tb.sort_values("q50", ascending=False)
        st.dataframe(tb.head(80), use_container_width=True)
else:
    st.info("No building_name column.")
