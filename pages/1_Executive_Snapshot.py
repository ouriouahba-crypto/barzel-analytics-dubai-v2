import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, selection_bar, apply_plotly_theme
from src.analytics.market_views import snapshot, snapshots_by
from src.analytics.kpi_engine import floor_weighted_price, price_timeseries_proxy
from src.analytics.advanced_kpis import typology_concentration, terrace_premium


hero("Executive Snapshot", "High-level view of key market metrics and dynamics.")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

# Selection bar (premium pattern)
districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = selection_bar(districts, label="Districts", default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

snap = snapshot(view)

# -------------------------
# KPI WALL (grouped) — FULL
# -------------------------
st.subheader("Key Metrics")

c1, c2, c3, c4, c5 = st.columns(5)
with c1: kpi_card("Listings", f"{snap['n_obs']:,}", "Sample size")
with c2: kpi_card("Median AED/sqm", f"{int(snap['median_price_sqm']):,}" if snap["median_price_sqm"] == snap["median_price_sqm"] else "n/a", "Pricing level")
with c3: kpi_card("Median DOM", f"{int(snap['median_dom']):,}" if snap["median_dom"] == snap["median_dom"] else "n/a", "Days to exit")
with c4: kpi_card("Net Yield (median)", f"{snap['net_yield_median']:.2f}%" if snap["net_yield_median"] == snap["net_yield_median"] else "n/a", "Income return")
with c5: kpi_card("Service Charge (median)", f"{int(snap['service_charge_median']):,}" if snap["service_charge_median"] == snap["service_charge_median"] else "n/a", "Annual cost")

c6, c7, c8, c9, c10 = st.columns(5)
with c6: kpi_card("Quick Sales ≤30d", f"{snap['fast_sale_ratio_30d']:.0%}" if snap["fast_sale_ratio_30d"] == snap["fast_sale_ratio_30d"] else "n/a", "Liquidity signal")
with c7: kpi_card("Quick Sales ≤60d", f"{snap['fast_sale_ratio_60d']:.0%}" if snap["fast_sale_ratio_60d"] == snap["fast_sale_ratio_60d"] else "n/a", "Liquidity signal")
with c8: kpi_card("Liquidity Depth", f"{snap['liquidity_depth_ratio']:.2f}" if snap["liquidity_depth_ratio"] == snap["liquidity_depth_ratio"] else "n/a", "n/DOM ratio")
with c9: kpi_card("Price Consistency", f"{snap['price_consistency_cv']:.3f}" if snap["price_consistency_cv"] == snap["price_consistency_cv"] else "n/a", "Variation (CV)")
# Format yield efficiency as percentage with 3 decimals for small ratios
yield_eff_display = f"{snap['yield_efficiency_ratio']*100:.3f}%" if snap["yield_efficiency_ratio"] == snap["yield_efficiency_ratio"] else "n/a"
with c10: kpi_card("Yield Efficiency", yield_eff_display, "Yield/Price ratio")

st.markdown("")

# -------------------------
# Charts row 1
# -------------------------
left, right = st.columns(2)

with left:
    d = view.dropna(subset=["price_per_sqm"])
    fig = px.histogram(d, x="price_per_sqm", nbins=40, title="Distribution: AED/sqm")
    fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Count")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

with right:
    d = view.dropna(subset=["days_on_market"])
    fig = px.histogram(d, x="days_on_market", nbins=40, title="Distribution: Days on Market")
    fig.update_layout(xaxis_title="Days on Market", yaxis_title="Count")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

st.markdown("")

# -------------------------
# Charts row 2: Price vs DOM
# -------------------------
st.subheader("Pricing Discipline")
d = view.dropna(subset=["price_per_sqm", "days_on_market"]).copy()
if len(d) < 30:
    st.info("Not enough data for scatter plot.")
else:
    fig = px.scatter(
        d,
        x="price_per_sqm",
        y="days_on_market",
        hover_data=[c for c in ["district", "bedrooms", "building_name", "size_sqm"] if c in d.columns],
        title="Price vs Time to Exit",
        opacity=0.55,
    )
    fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Days on Market")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

st.markdown("")

# -------------------------
# Floor premium (weighted)
# -------------------------
st.subheader("Floor Premium Analysis")
fp = floor_weighted_price(view)
if fp.empty:
    st.info("Insufficient data for floor premium analysis.")
else:
    fig = px.line(fp, x="floor_bucket", y="weighted_price_sqm", markers=True, title="Weighted Price by Floor")
    fig.update_layout(xaxis_title="Floor range", yaxis_title="AED per sqm (weighted)")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

st.markdown("")

# -------------------------
# Price dynamics proxy
# -------------------------
st.subheader("Price Dynamics")
ts = price_timeseries_proxy(view)
if ts.empty:
    st.info("Insufficient data for price time series.")
else:
    fig = px.line(ts, x="month", y="median_price_sqm", markers=True, title="Monthly Median Price Trend")
    fig.update_layout(xaxis_title="Month", yaxis_title="Median AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

st.markdown("")

# -------------------------
# Typology composition
# -------------------------
st.subheader("Market Composition by Type")
tc = typology_concentration(view)
if not tc.empty:
    fig = px.pie(tc, names="bedrooms", values="count", title="Product Mix (Bedrooms)")
    fig.update_traces(hole=0.45)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5))
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

st.markdown("")

# -------------------------
# Terrace premium
# -------------------------
st.subheader("Terrace Premium")
tp = terrace_premium(view)
c1, c2 = st.columns(2)
with c1: kpi_card("Absolute Premium", f"{tp['premium_abs']:.0f} AED/sqm" if tp["premium_abs"] == tp["premium_abs"] else "n/a", "Terrace uplift")
with c2: kpi_card("Relative Premium", f"{tp['premium_pct']:.1%}" if tp["premium_pct"] == tp["premium_pct"] else "n/a", "Terrace uplift")

st.divider()

# -------------------------
# District table (enriched)
# -------------------------
st.subheader("District Summary")
table = snapshots_by(view, "district")
if table.empty:
    st.info("No district data available.")
else:
    table = table.sort_values("n_obs", ascending=False)
    st.dataframe(table, use_container_width=True)
