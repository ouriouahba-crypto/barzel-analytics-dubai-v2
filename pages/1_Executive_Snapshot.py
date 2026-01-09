import streamlit as st
import plotly.express as px

from src.app.ui import hero
from src.analytics.market_views import snapshot, snapshots_by
from src.analytics.kpi_engine import floor_weighted_price, price_timeseries_proxy
from src.analytics.advanced_kpis import typology_concentration, terrace_premium


hero("Executive Snapshot", "High-level analytics cockpit (no score, no decision).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

st.caption("All metrics are descriptive. Scores exist only in the PDF memo.")

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

snap = snapshot(view)

# -------------------------
# KPI WALL (grouped)
# -------------------------
st.subheader("Key metrics (descriptive)")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Listings", f"{snap['n_obs']:,}")
c2.metric("Median AED/sqm", f"{int(snap['median_price_sqm']):,}" if snap["median_price_sqm"] == snap["median_price_sqm"] else "n/a")
c3.metric("Median DOM", f"{int(snap['median_dom']):,}" if snap["median_dom"] == snap["median_dom"] else "n/a")
c4.metric("Net yield (median)", f"{snap['net_yield_median']:.2f}%" if snap["net_yield_median"] == snap["net_yield_median"] else "n/a")
c5.metric("Service charge (median)", f"{int(snap['service_charge_median']):,}" if snap["service_charge_median"] == snap["service_charge_median"] else "n/a")

c6, c7, c8, c9, c10 = st.columns(5)
c6.metric("Fast-sale ≤30d", f"{snap['fast_sale_ratio_30d']:.0%}" if snap["fast_sale_ratio_30d"] == snap["fast_sale_ratio_30d"] else "n/a")
c7.metric("Fast-sale ≤60d", f"{snap['fast_sale_ratio_60d']:.0%}" if snap["fast_sale_ratio_60d"] == snap["fast_sale_ratio_60d"] else "n/a")
c8.metric("Liquidity depth (n/DOM)", f"{snap['liquidity_depth_ratio']:.2f}" if snap["liquidity_depth_ratio"] == snap["liquidity_depth_ratio"] else "n/a")
c9.metric("Price consistency (CV)", f"{snap['price_consistency_cv']:.3f}" if snap["price_consistency_cv"] == snap["price_consistency_cv"] else "n/a")
c10.metric("Yield efficiency", f"{snap['yield_efficiency_ratio']:.6f}" if snap["yield_efficiency_ratio"] == snap["yield_efficiency_ratio"] else "n/a")

st.divider()

# -------------------------
# Charts row 1
# -------------------------
left, right = st.columns(2)

with left:
    d = view.dropna(subset=["price_per_sqm"])
    fig = px.histogram(d, x="price_per_sqm", nbins=40, title="Distribution: AED/sqm")
    fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

with right:
    d = view.dropna(subset=["days_on_market"])
    fig = px.histogram(d, x="days_on_market", nbins=40, title="Distribution: Days on Market")
    fig.update_layout(xaxis_title="Days on Market", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -------------------------
# Charts row 2: Price vs DOM (discipline)
# -------------------------
st.subheader("Pricing discipline (price vs time-to-exit)")
d = view.dropna(subset=["price_per_sqm", "days_on_market"]).copy()
if len(d) < 30:
    st.info("Not enough data for a price vs DOM scatter.")
else:
    fig = px.scatter(
        d,
        x="price_per_sqm",
        y="days_on_market",
        hover_data=[c for c in ["district", "bedrooms", "building_name", "size_sqm"] if c in d.columns],
        title="Scatter: AED/sqm vs Days on Market",
        opacity=0.55,
    )
    fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Days on Market")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -------------------------
# Floor premium (weighted)
# -------------------------
st.subheader("Floor premium (weighted by sqm)")
fp = floor_weighted_price(view)
if fp.empty:
    st.info("Not enough data for floor premium.")
else:
    fig = px.line(fp, x="floor", y="weighted_price_sqm", markers=True, title="Weighted AED/sqm by floor")
    fig.update_layout(xaxis_title="Floor", yaxis_title="Weighted AED per sqm")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -------------------------
# Price dynamics proxy
# -------------------------
st.subheader("Price dynamics (proxy from first_seen)")
ts = price_timeseries_proxy(view)
if ts.empty:
    st.info("Not enough data for a time series proxy.")
else:
    fig = px.line(ts, x="month", y="median_price_sqm", markers=True, title="Monthly median AED/sqm (proxy)")
    fig.update_layout(xaxis_title="Month", yaxis_title="Median AED per sqm")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -------------------------
# Typology composition
# -------------------------
st.subheader("Typology composition")
tc = typology_concentration(view)
fig = px.pie(tc, names="bedrooms", values="count", title="Market composition (by bedrooms)")
st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Terrace premium
# -------------------------
st.subheader("Terrace premium (if coverage allows)")
tp = terrace_premium(view)
c1, c2 = st.columns(2)
c1.metric("Terrace premium (abs AED/sqm)", f"{tp['premium_abs']:.0f}" if tp["premium_abs"] == tp["premium_abs"] else "n/a")
c2.metric("Terrace premium (%)", f"{tp['premium_pct']:.1%}" if tp["premium_pct"] == tp["premium_pct"] else "n/a")

st.divider()

# -------------------------
# District table (enriched)
# -------------------------
st.subheader("District table (descriptive, enriched)")
table = snapshots_by(view, "district")
if table.empty:
    st.info("No district table available.")
else:
    table = table.sort_values("n_obs", ascending=False)
    st.dataframe(table, use_container_width=True)
