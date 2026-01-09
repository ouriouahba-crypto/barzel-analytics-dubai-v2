import streamlit as st
import plotly.express as px

from src.app.ui import hero
from src.analytics.aggregations import group_stats


hero("Liquidity & Negotiation", "Exit speed, market discipline, and spreads (if available).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel_d = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel_d)] if sel_d else df

st.divider()

# DOM distribution
st.subheader("Days on Market distribution")
d = view.dropna(subset=["days_on_market"])
if len(d) < 20:
    st.info("Not enough DOM data.")
else:
    fig = px.histogram(d, x="days_on_market", nbins=40, title="DOM distribution")
    fig.update_layout(xaxis_title="Days on Market", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# DOM by bedrooms
st.subheader("DOM by bedrooms (median)")
if "bedrooms" in view.columns:
    t = group_stats(view, ["district","bedrooms"], "days_on_market", min_n=10)
    if t.empty:
        st.info("Not enough data.")
    else:
        fig = px.line(t.sort_values(["district","bedrooms"]), x="bedrooms", y="q50", color="district", markers=True, title="Median DOM by bedrooms")
        fig.update_layout(xaxis_title="Bedrooms", yaxis_title="Median DOM")
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# Pricing discipline: price vs DOM
st.subheader("Pricing discipline (AED/sqm vs DOM)")
d = view.dropna(subset=["price_per_sqm","days_on_market"])
if len(d) < 30:
    st.info("Not enough data.")
else:
    fig = px.scatter(
        d,
        x="price_per_sqm",
        y="days_on_market",
        color="district" if "district" in d.columns else None,
        opacity=0.45,
        hover_data=[c for c in ["bedrooms","building_name","size_sqm","floor"] if c in d.columns],
        title="Scatter: AED/sqm vs DOM"
    )
    fig.update_layout(xaxis_title="AED/sqm", yaxis_title="Days on Market")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Spread (if column exists)
spread_cols = [c for c in ["ask_vs_sale_spread_pct", "ask_to_sale_spread_pct"] if c in view.columns]
if spread_cols:
    sc = spread_cols[0]
    st.subheader("Ask vs Sale spread (if available)")
    s = view.dropna(subset=[sc])
    fig = px.histogram(s, x=sc, nbins=40, title=f"Distribution: {sc}")
    fig.update_layout(xaxis_title="Spread (%)", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No spread column found in CSV (ask_vs_sale_spread_pct).")
