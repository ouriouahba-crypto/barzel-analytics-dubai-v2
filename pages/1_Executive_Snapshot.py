import streamlit as st
import plotly.express as px
import pandas as pd

from src.app.ui import (
    hero, kpi_card, selection_bar, apply_plotly_theme,
    executive_summary, section_intro, takeaway, metric_group_label
)
from src.analytics.market_views import snapshot, snapshots_by
from src.analytics.kpi_engine import floor_weighted_price, price_timeseries_proxy
from src.analytics.advanced_kpis import typology_concentration, terrace_premium

hero("Executive Snapshot", "Market overview with key pricing, liquidity, and income indicators.")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

# Selection bar (premium pattern)
districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = selection_bar(districts, label="Districts", default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

snap = snapshot(view)

# ===== EXECUTIVE SUMMARY BLOCK =====
insights = []
if snap['n_obs'] > 0:
    insights.append(f"Market sample includes {snap['n_obs']:,} listings across {len(view['district'].unique()) if 'district' in view.columns else 1} district(s).")
if snap["median_price_sqm"] == snap["median_price_sqm"]:
    insights.append(f"Median pricing at {int(snap['median_price_sqm']):,} AED/sqm suggests a {('premium' if snap['median_price_sqm'] > 4000 else 'moderate' if snap['median_price_sqm'] > 2000 else 'value')} market positioning.")
if snap["median_dom"] == snap["median_dom"]:
    insights.append(f"Median time-to-exit of {int(snap['median_dom'])} days indicates {'strong' if snap['median_dom'] < 60 else 'moderate' if snap['median_dom'] < 120 else 'slower'} liquidity.")
if snap["net_yield_median"] == snap["net_yield_median"]:
    insights.append(f"Median net yield at {snap['net_yield_median']:.2f}% reflects current rental income dynamics relative to property values.")
if snap["price_consistency_cv"] == snap["price_consistency_cv"]:
    insights.append(f"Price dispersion (CV: {snap['price_consistency_cv']:.2f}) indicates {'tight' if snap['price_consistency_cv'] < 0.2 else 'moderate' if snap['price_consistency_cv'] < 0.35 else 'wide'} valuation variation across the portfolio.")

if insights:
    executive_summary(insights)

st.divider()

# ===== GROUPED KPIs =====
metric_group_label("Coverage & Data Quality")
c1, c2, c3 = st.columns(3)
with c1: kpi_card("Sample Size", f"{snap['n_obs']:,}", "Active listings")
with c2: kpi_card("Districts", f"{len(view['district'].unique())}" if "district" in view.columns else "1", "Selected")
with c3: kpi_card("Data Completeness", f"{(view[['price_per_sqm', 'days_on_market']].notna().mean().mean() * 100):.0f}%", "Key fields")

metric_group_label("Pricing Market")
c1, c2, c3 = st.columns(3)
with c1: kpi_card("Median Price", f"{int(snap['median_price_sqm']):,}" if snap["median_price_sqm"] == snap["median_price_sqm"] else "n/a", "AED/sqm")
with c2: kpi_card("Price Variation", f"{snap['price_consistency_cv']:.2f}" if snap["price_consistency_cv"] == snap["price_consistency_cv"] else "n/a", "Coefficient of Variation")
with c3: kpi_card("P90 Threshold", f"{view['price_per_sqm'].quantile(0.9):.0f}" if 'price_per_sqm' in view.columns else "n/a", "90th percentile")

metric_group_label("Liquidity & Exit Dynamics")
c1, c2, c3 = st.columns(3)
with c1: kpi_card("Median Time-to-Exit", f"{int(snap['median_dom']):,}" if snap["median_dom"] == snap["median_dom"] else "n/a", "Days")
with c2: kpi_card("Quick Sales ≤30d", f"{snap['fast_sale_ratio_30d']:.0%}" if snap["fast_sale_ratio_30d"] == snap["fast_sale_ratio_30d"] else "n/a", "% of units")
with c3: kpi_card("Liquidity Depth", f"{snap['liquidity_depth_ratio']:.2f}" if snap["liquidity_depth_ratio"] == snap["liquidity_depth_ratio"] else "n/a", "listings/median DOM")

metric_group_label("Yield & Income")
c1, c2 = st.columns(2)
with c1: kpi_card("Median Net Yield", f"{snap['net_yield_median']:.2f}%" if snap["net_yield_median"] == snap["net_yield_median"] else "n/a", "Annual return")
with c2: kpi_card("Yield Efficiency", f"{snap['yield_efficiency_ratio']*100:.3f}%" if snap["yield_efficiency_ratio"] == snap["yield_efficiency_ratio"] else "n/a", "Yield/Price ratio")

metric_group_label("Operating Costs")
c1, c2 = st.columns(2)
with c1: kpi_card("Annual Service Charge", f"{int(snap['service_charge_median']):,}" if snap["service_charge_median"] == snap["service_charge_median"] else "n/a", "AED/sqm/yr median")
with c2: kpi_card("Service Charge Impact", f"{((snap['service_charge_median'] / (snap['median_price_sqm'] * 0.05)) * 100):.1f}%" if (snap["service_charge_median"] == snap["service_charge_median"] and snap["median_price_sqm"] == snap["median_price_sqm"]) else "n/a", "Estimated % of yield")

st.divider()

# ===== PRICING ANALYSIS =====
section_intro("Pricing Distribution Analysis", "Understanding the breadth of pricing across the market.")
left, right = st.columns(2)

with left:
    d = view.dropna(subset=["price_per_sqm"])
    if len(d) > 0:
        fig = px.histogram(d, x="price_per_sqm", nbins=40, title="Price Distribution Across Selected Districts")
        fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Listing Count")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
        takeaway(f"Distribution reveals {(d['price_per_sqm'] > d['price_per_sqm'].quantile(0.75)).sum()} listings above the 75th percentile, indicating concentrated premium inventory.")

with right:
    d = view.dropna(subset=["days_on_market"])
    if len(d) > 0:
        fig = px.histogram(d, x="days_on_market", nbins=40, title="Time-to-Exit Distribution")
        fig.update_layout(xaxis_title="Days on Market", yaxis_title="Listing Count")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
        takeaway(f"Fast sales (≤30 days) represent {snap['fast_sale_ratio_30d']:.0%} of market, signaling {'robust' if snap['fast_sale_ratio_30d'] > 0.25 else 'moderate'} liquidity.")

st.divider()

# ===== PRICE-TIME RELATIONSHIP =====
section_intro("Pricing Discipline Analysis", "Relationship between asking price and time-to-exit.")
d = view.dropna(subset=["price_per_sqm", "days_on_market"]).copy()
if len(d) < 30:
    st.info("Insufficient data for pricing discipline analysis.")
else:
    fig = px.scatter(
        d,
        x="price_per_sqm",
        y="days_on_market",
        hover_data=[c for c in ["district", "bedrooms", "building_name", "size_sqm"] if c in d.columns],
        title="Price vs. Market Exit Speed (Disciplined Markets Show Negative Correlation)",
        opacity=0.6,
    )
    fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Days on Market")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    corr = d['price_per_sqm'].corr(d['days_on_market'])
    correlation_signal = "stronger" if abs(corr) > 0.3 else "moderate" if abs(corr) > 0.15 else "weaker"
    takeaway(f"Correlation of {corr:.2f} suggests {correlation_signal} pricing discipline: {'evidence of overpricing issues' if corr > 0.1 else 'market pricing appears relatively efficient'}")

st.divider()

# ===== FLOOR PREMIUM ANALYSIS =====
section_intro("Vertical Market Premium", "How price varies by floor band (weighted by unit size).")
fp = floor_weighted_price(view)
if fp.empty:
    st.info("Floor premium analysis unavailable (insufficient data with floor information).")
else:
    fig = px.line(fp, x="floor_bucket", y="weighted_price_sqm", markers=True, 
                  title="Weighted Price by Floor Band", line_shape="spline")
    fig.update_layout(xaxis_title="Floor Band", yaxis_title="Weighted AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    if len(fp) > 1:
        max_floor = fp.loc[fp['weighted_price_sqm'].idxmax()]
        min_floor = fp.loc[fp['weighted_price_sqm'].idxmin()]
        premium_pct = ((max_floor['weighted_price_sqm'] - min_floor['weighted_price_sqm']) / min_floor['weighted_price_sqm'] * 100)
        takeaway(f"Upper floors command a {premium_pct:.1f}% premium over lower floors, reflecting view and amenity preferences.")

st.divider()

# ===== PRICE TREND ANALYSIS =====
section_intro("Temporal Pricing Trend", "How market pricing has evolved over the observation period.")
ts = price_timeseries_proxy(view)
if ts.empty:
    st.info("Pricing trend analysis unavailable (insufficient historical data).")
else:
    fig = px.line(ts, x="month", y="median_price_sqm", markers=True, title="Monthly Median Pricing Trend",
                  line_shape="spline")
    fig.update_layout(xaxis_title="Month", yaxis_title="Median AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    if len(ts) > 1:
        first_price = ts.iloc[0]['median_price_sqm']
        last_price = ts.iloc[-1]['median_price_sqm']
        trend_pct = ((last_price - first_price) / first_price * 100)
        trend_dir = "strengthening" if trend_pct >= 0 else "softening"
        takeaway(f"Median pricing shows {trend_dir} dynamics ({trend_pct:+.1f}%), reflecting evolving market conditions over the period.")

st.divider()

# ===== PRODUCT MIX ANALYSIS =====
section_intro("Product Mix & Market Composition", "Distribution of inventory by bedrooms and unit type.")
tc = typology_concentration(view)
if not tc.empty:
    fig = px.pie(tc, names="bedrooms", values="count", title="Market Distribution by Bedroom Count (Donut View)")
    fig.update_traces(hole=0.40, textposition='inside', textinfo='label+percent')
    fig.update_layout(
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
        margin=dict(r=200)
    )
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    largest_segment = tc.loc[tc['count'].idxmax()]
    takeaway(f"{largest_segment['bedrooms']}-bedroom units comprise {(largest_segment['count']/tc['count'].sum()*100):.0f}% of the portfolio, indicating dominant product preference.")
else:
    st.info("Product mix analysis unavailable.")

st.divider()

# ===== TERRACE PREMIUM =====
section_intro("Terrace & Special Features", "Premium pricing for units with terraces or special features.")
tp = terrace_premium(view)
c1, c2 = st.columns(2)
with c1: kpi_card("Terrace Price Premium (AED/sqm)", f"{tp['premium_abs']:.0f}" if tp["premium_abs"] == tp["premium_abs"] else "n/a", "Absolute uplift")
with c2: kpi_card("Terrace Price Premium (%)", f"{tp['premium_pct']:.1%}" if tp["premium_pct"] == tp["premium_pct"] else "n/a", "Relative uplift")

st.divider()

# ===== DISTRICT SUMMARY TABLE =====
section_intro("District-Level Summary", "Comparative metrics across selected districts for quick benchmarking.")
table = snapshots_by(view, "district")
if table.empty:
    st.info("District summary unavailable.")
else:
    table = table.sort_values("n_obs", ascending=False)
    display_cols = {
        'n_obs': 'Listings',
        'median_price_sqm': 'Median Price (AED/sqm)',
        'median_dom': 'Median DOM (days)',
        'net_yield_median': 'Median Yield (%)',
        'service_charge_median': 'Service Charge (AED/sqm/yr)',
        'price_consistency_cv': 'Price Variation (CV)',
        'fast_sale_ratio_30d': 'Quick Sales ≤30d (%)',
    }
    display_table = table[[col for col in display_cols.keys() if col in table.columns]].copy()
    display_table.columns = [display_cols.get(col, col) for col in display_table.columns]
    
    for col in display_table.columns:
        if 'AED' in col or 'Price' in col or 'Service' in col:
            display_table[col] = display_table[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "n/a")
        elif '%' in col or 'Yield' in col or 'Quick' in col:
            display_table[col] = display_table[col].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "n/a")
        elif 'CV' in col or 'Variation' in col:
            display_table[col] = display_table[col].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "n/a")
        elif 'DOM' in col:
            display_table[col] = display_table[col].apply(lambda x: f"{int(x)}" if pd.notna(x) else "n/a")
    
    st.dataframe(display_table, use_container_width=True)
