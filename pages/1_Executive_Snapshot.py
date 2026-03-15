import streamlit as st
import plotly.express as px
import pandas as pd

from src.app.ui import (
    hero, kpi_card, selection_bar, apply_plotly_theme,
    executive_summary, section_intro, takeaway, metric_group_label,
    chart_explanation, premium_insight
)
from src.app.translations import get_text
from src.analytics.market_views import snapshot, snapshots_by
from src.analytics.kpi_engine import floor_weighted_price, price_timeseries_proxy
from src.analytics.advanced_kpis import typology_concentration, terrace_premium

lang = st.session_state.get("language", "en")

hero(get_text("exec_snapshot_title", lang), get_text("exec_snapshot_subtitle", lang))

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

# Selection bar (premium pattern)
districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = selection_bar(districts, label=get_text("label_districts", lang), default=districts[:3] if len(districts) >= 3 else districts)
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
metric_group_label(get_text("metric_group_coverage", lang))
c1, c2, c3 = st.columns(3)
with c1: kpi_card(get_text("kpi_sample_size", lang), f"{snap['n_obs']:,}", get_text("active_listings", lang))
with c2: kpi_card(get_text("kpi_districts", lang), f"{len(view['district'].unique())}" if "district" in view.columns else "1", get_text("selected", lang))
with c3: kpi_card(get_text("kpi_data_completeness", lang), f"{(view[['price_per_sqm', 'days_on_market']].notna().mean().mean() * 100):.0f}%", get_text("key_fields", lang))

metric_group_label(get_text("metric_group_pricing", lang))
c1, c2, c3 = st.columns(3)
with c1: kpi_card(get_text("kpi_median_price", lang), f"{int(snap['median_price_sqm']):,}" if snap["median_price_sqm"] == snap["median_price_sqm"] else "n/a", get_text("aed_sqm", lang))
with c2: kpi_card(get_text("price_variation", lang), f"{snap['price_consistency_cv']:.2f}" if snap["price_consistency_cv"] == snap["price_consistency_cv"] else "n/a", get_text("coefficient_variation", lang))
with c3: kpi_card(get_text("p90_threshold", lang), f"{view['price_per_sqm'].quantile(0.9):.0f}" if 'price_per_sqm' in view.columns else "n/a", get_text("percentile_90", lang))

metric_group_label(get_text("metric_group_liquidity", lang))
c1, c2, c3 = st.columns(3)
with c1: kpi_card(get_text("chart_median_exit", lang), f"{int(snap['median_dom']):,}" if snap["median_dom"] == snap["median_dom"] else "n/a", get_text("days_unit", lang))
with c2: kpi_card(get_text("chart_quick_sales", lang), f"{snap['fast_sale_ratio_30d']:.0%}" if snap["fast_sale_ratio_30d"] == snap["fast_sale_ratio_30d"] else "n/a", "% of units")
with c3: kpi_card("Liquidity Depth", f"{snap['liquidity_depth_ratio']:.2f}" if snap["liquidity_depth_ratio"] == snap["liquidity_depth_ratio"] else "n/a", "listings/median DOM")

metric_group_label(get_text("metric_group_yield", lang))
c1, c2 = st.columns(2)
with c1: kpi_card(get_text("chart_median_net_yield", lang), f"{snap['net_yield_median']:.2f}%" if snap["net_yield_median"] == snap["net_yield_median"] else "n/a", "Annual return")
with c2: kpi_card("Yield Efficiency", f"{snap['yield_efficiency_ratio']*100:.3f}%" if snap["yield_efficiency_ratio"] == snap["yield_efficiency_ratio"] else "n/a", "Yield/Price ratio")

metric_group_label(get_text("metric_group_costs", lang))
c1, c2 = st.columns(2)
with c1: kpi_card(get_text("chart_service_charge", lang), f"{int(snap['service_charge_median']):,}" if snap["service_charge_median"] == snap["service_charge_median"] else "n/a", get_text("aed_sqm_year", lang))
with c2: kpi_card("Service Charge Impact", f"{((snap['service_charge_median'] / (snap['median_price_sqm'] * 0.05)) * 100):.1f}%" if (snap["service_charge_median"] == snap["service_charge_median"] and snap["median_price_sqm"] == snap["median_price_sqm"]) else "n/a", "Estimated % of yield")

st.divider()

# ===== PRICING ANALYSIS =====
section_intro(get_text("pricing_distribution_title", lang), get_text("pricing_distribution_subtitle", lang))
chart_explanation(get_text("chart_dist_explanation", lang))
left, right = st.columns(2)

with left:
    d = view.dropna(subset=["price_per_sqm"])
    if len(d) > 0:
        fig = px.histogram(d, x="price_per_sqm", nbins=40, title="Price Distribution Across Districts")
        fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Listing Count")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
        premium_units = (d['price_per_sqm'] > d['price_per_sqm'].quantile(0.75)).sum()
        premium_insight(f"Premium segment concentration: {premium_units} listings ({premium_units/len(d)*100:.0f}% of sample) are priced above the 75th percentile, indicating meaningful high-end inventory.", "📊")

with right:
    d = view.dropna(subset=["days_on_market"])
    if len(d) > 0:
        fig = px.histogram(d, x="days_on_market", nbins=40, title="Market Exit Speed Distribution")
        fig.update_layout(xaxis_title="Days on Market", yaxis_title="Listing Count")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
        quick_sales_pct = snap['fast_sale_ratio_30d']
        liquidity_signal = 'very strong' if quick_sales_pct > 0.35 else 'strong' if quick_sales_pct > 0.25 else 'moderate'
        premium_insight(f"Liquidity signal: {quick_sales_pct:.0%} of properties sell within 30 days, reflecting {liquidity_signal} market absorption capacity.", "⚡")

st.divider()

# ===== PRICE-TIME RELATIONSHIP =====
section_intro(get_text("pricing_discipline_title", lang), get_text("pricing_discipline_subtitle", lang))
chart_explanation(get_text("discipline_explanation", lang))
d = view.dropna(subset=["price_per_sqm", "days_on_market"]).copy()
if len(d) < 30:
    st.info("Insufficient data for pricing discipline analysis.")
else:
    fig = px.scatter(
        d,
        x="price_per_sqm",
        y="days_on_market",
        hover_data=[c for c in ["district", "bedrooms", "building_name", "size_sqm"] if c in d.columns],
        title="Price vs. Market Exit Speed",
        opacity=0.6,
    )
    fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Days on Market")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    corr = d['price_per_sqm'].corr(d['days_on_market'])
    if corr > 0.1:
        insight_msg = "positive correlation signals potential overpricing of higher-end units"
    elif corr < -0.1:
        insight_msg = "negative correlation indicates disciplined pricing across market segments"
    else:
        insight_msg = "weak correlation suggests pricing independence from absorption rates"
    premium_insight(f"Market efficiency: {corr:+.2f} correlation — {insight_msg}.", "🎯")

st.divider()

# ===== FLOOR PREMIUM ANALYSIS =====
section_intro("Vertical Market Premium", "How price varies by floor band (weighted by unit size).")
chart_explanation("This line chart maps the weighted average price per sqm across floor bands. It shows whether upper floors command premium valuations due to views, amenities, and prestige — a key driver of value in high-rise markets.")
fp = floor_weighted_price(view)
if fp.empty:
    st.info("Floor premium analysis unavailable (insufficient data with floor information).")
else:
    fig = px.line(fp, x="floor_bucket", y="weighted_price_sqm", markers=True, 
                  title="Price Premium by Floor Band", line_shape="spline")
    fig.update_layout(xaxis_title="Floor Band", yaxis_title="Weighted AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    if len(fp) > 1:
        max_floor = fp.loc[fp['weighted_price_sqm'].idxmax()]
        min_floor = fp.loc[fp['weighted_price_sqm'].idxmin()]
        premium_pct = ((max_floor['weighted_price_sqm'] - min_floor['weighted_price_sqm']) / min_floor['weighted_price_sqm'] * 100)
        premium_insight(f"Vertical stratification: Properties in {max_floor['floor_bucket']} command a {premium_pct:.1f}% premium relative to {min_floor['floor_bucket']}, reflecting strong amenity valuation.", "🏢")

st.divider()

# ===== PRICE TREND ANALYSIS =====
section_intro("Temporal Pricing Trend", "How market pricing has evolved over the observation period.")
chart_explanation("This line chart tracks median asking prices on a monthly basis. Upward trends indicate strengthening market conditions and limited supply, while downward trends may signal increased supply, weaker demand, or market corrections.")
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
        trend_dir = "strengthening" if trend_pct > 2 else "weakening" if trend_pct < -2 else "stable"
        premium_insight(f"Market trajectory: Median pricing is {trend_dir} ({trend_pct:+.1f}% over period), reflecting {('supply-constrained strength' if trend_pct > 0 else 'normalization pressures')}.", "📈")

st.divider()

# ===== PRODUCT MIX ANALYSIS =====
section_intro("Product Mix & Market Composition", "Distribution of inventory by bedrooms and unit type.")
chart_explanation("This donut chart visualizes how your portfolio is composed across bedroom counts. Understanding product mix is critical for identifying concentration risk and assessing whether your holdings align with target market segments.")
tc = typology_concentration(view)
if not tc.empty:
    fig = px.pie(tc, names="bedrooms", values="count", title="Inventory Distribution by Bedroom Count")
    fig.update_traces(hole=0.40, textposition='inside', textinfo='label+percent')
    fig.update_layout(
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
        margin=dict(r=200)
    )
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    largest_segment = tc.loc[tc['count'].idxmax()]
    concentration = (largest_segment['count']/tc['count'].sum()*100)
    premium_insight(f"Product concentration: {largest_segment['bedrooms']}-bedroom units represent {concentration:.0f}% of inventory, indicating {'significant concentration risk' if concentration > 50 else 'balanced portfolio diversification'}.", "🔍")
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
