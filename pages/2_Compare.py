import streamlit as st
import plotly.express as px
import pandas as pd

from src.app.ui import (
    hero, kpi_card, selection_bar, apply_plotly_theme,
    section_intro, takeaway, metric_group_label
)
from src.analytics.market_views import snapshots_by


hero("Compare", "Side-by-side cross-district analysis and competitive positioning.")

df = st.session_state.get("df")
if df is None or df.empty or "district" not in df.columns:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist())
sel = selection_bar(districts, label="Districts", default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

g = snapshots_by(view, "district")
if g.empty:
    st.info("Not enough data for comparison.")
    st.stop()

# ===== COMPARATIVE SUMMARY =====
section_intro("What Stands Out Across Selected Districts", "Key competitive findings and relative positioning.")

# Identify leaders/laggards for narrative
most_expensive = g.loc[g['median_price_sqm'].idxmax()]
most_affordable = g.loc[g['median_price_sqm'].idxmin()]
most_liquid = g.loc[g['median_dom'].idxmin()]
best_yields = g.loc[g['net_yield_median'].idxmax()]
lowest_costs = g.loc[g['service_charge_median'].idxmin()]

summary_points = [
    f"Pricing ranges from {int(most_affordable['median_price_sqm']):,} (floors: {most_affordable.name}) to {int(most_expensive['median_price_sqm']):,} AED/sqm ({most_expensive.name}), reflecting {((most_expensive['median_price_sqm'] / most_affordable['median_price_sqm'] - 1) * 100):.0f}% market segmentation.",
    f"Most liquid market: {most_liquid.name} exits in median {int(most_liquid['median_dom'])} days. Slowest: {g.loc[g['median_dom'].idxmax()].name} ({int(g['median_dom'].max())} days).",
    f"Yield spreads across portfolio: {best_yields.name} ({best_yields['net_yield_median']:.2f}%) vs lowest ({g['net_yield_median'].min():.2f}%).",
    f"Operating cost efficiency: {lowest_costs.name} charges {int(lowest_costs['service_charge_median']):,} AED/sqm/yr vs {int(g['service_charge_median'].max()):,} in highest-cost district.",
]

for point in summary_points[:3]:
    st.markdown(f"• {point}")

st.divider()

# ===== TOP KPIS =====
c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Districts Compared", f"{len(g):,}", "In selection")
with c2: kpi_card("Total Market Size", f"{int(g['n_obs'].sum()):,}", "Active listings")
with c3: kpi_card("Price Premium Spread", f"{((most_expensive['median_price_sqm'] / most_affordable['median_price_sqm']) - 1):.0%}", "High vs Low")
with c4: kpi_card("Liquidity Range", f"{int(g['median_dom'].max() - g['median_dom'].min())} days", "Max - Min DOM")

st.divider()

# ===== DISTRICT SUMMARY TABLE =====
section_intro("Complete District Benchmarking", "All metrics for comparative analysis.")
table_sorted = g.sort_values("n_obs", ascending=False)
display_cols = {
    'n_obs': 'Listings',
    'median_price_sqm': 'Median Price (AED/sqm)',
    'median_dom': 'Median DOM (days)',
    'net_yield_median': 'Median Yield (%)',
    'service_charge_median': 'Service Charge (AED/sqm/yr)',
    'fast_sale_ratio_30d': 'Quick Sales ≤30d (%)',
    'price_consistency_cv': 'Price Variation (CV)',
}
display_table = table_sorted[[col for col in display_cols.keys() if col in table_sorted.columns]].copy()
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

st.divider()

st.divider()

# ===== PRICING COMPARISON =====
section_intro("Pricing Landscape", "Median AED/sqm across districts reveals market segmentation.")
c1, c2 = st.columns(2)

with c1:
    fig = px.bar(g.sort_values("median_price_sqm", ascending=False), x=g.sort_values("median_price_sqm", ascending=False).index, 
                 y="median_price_sqm", title="Median Price by District (Ranked)")
    fig.update_layout(xaxis_title="District", yaxis_title="Median AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    price_spread = ((g['median_price_sqm'].max() - g['median_price_sqm'].min()) / g['median_price_sqm'].mean())
    takeaway(f"Price variance (±{price_spread:.0%} of mean) suggests {'distinct market segments' if price_spread > 0.20 else 'relatively homogeneous pricing'} across districts.")

with c2:
    fig = px.box(view.dropna(subset=['district', 'price_per_sqm']), x="district", y="price_per_sqm", 
                 title="Pricing Distribution by District (Box Plot)")
    fig.update_layout(xaxis_title="District", yaxis_title="AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    takeaway(f"Outlier presence and box heights indicate {'uniform' if view.groupby('district')['price_per_sqm'].std().mean() < 500 else 'heterogeneous'} pricing discipline within each district.")

st.divider()

# ===== LIQUIDITY COMPARISON =====
section_intro("Market Liquidity & Exit Dynamics", "Days-on-market reveals relative market depth and absorption capacity.")
c1, c2 = st.columns(2)

with c1:
    fig = px.bar(g.sort_values("median_dom"), x=g.sort_values("median_dom").index, y="median_dom", 
                 title="Median Time-to-Exit by District")
    fig.update_layout(xaxis_title="District", yaxis_title="Days on Market")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    fastest = g['median_dom'].min()
    slowest = g['median_dom'].max()
    takeaway(f"Liquidity delta: {int(slowest - fastest)} days between fastest ({int(fastest)}d) and slowest ({int(slowest)}d) markets.")

with c2:
    fig = px.bar(g.sort_values("fast_sale_ratio_30d", ascending=False), 
                 x=g.sort_values("fast_sale_ratio_30d", ascending=False).index, 
                 y="fast_sale_ratio_30d", 
                 title="Quick Sales (≤30 days) by District")
    fig.update_layout(xaxis_title="District", yaxis_title="% of Units")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    avg_quick_ratio = g['fast_sale_ratio_30d'].mean()
    takeaway(f"Average quick-sale ratio: {avg_quick_ratio:.0%}. Districts above this threshold show {'stronger' if avg_quick_ratio > 0.20 else 'moderate'} buyer momentum.")

st.divider()

# ===== YIELD COMPARISON =====
section_intro("Income Return Profile", "Net yields reflect rental market dynamics relative to acquisition prices.")
c1, c2 = st.columns(2)

with c1:
    fig = px.bar(g.sort_values("net_yield_median", ascending=False), 
                 x=g.sort_values("net_yield_median", ascending=False).index, 
                 y="net_yield_median", 
                 title="Median Net Yield by District")
    fig.update_layout(xaxis_title="District", yaxis_title="Net Yield (%)")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    yield_range = g['net_yield_median'].max() - g['net_yield_median'].min()
    takeaway(f"Yield dispersion of {yield_range:.2f}% reflects different rental market maturities across districts.")

with c2:
    fig = px.scatter(g, x="median_price_sqm", y="net_yield_median", 
                     hover_data=[g.index], size='n_obs',
                     title="Price vs. Yield Trade-off")
    fig.update_layout(xaxis_title="Median Price (AED/sqm)", yaxis_title="Net Yield (%)")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    corr_price_yield = g['median_price_sqm'].corr(g['net_yield_median'])
    takeaway(f"Price-yield correlation ({corr_price_yield:.2f}) indicates {'inverse' if corr_price_yield < -0.3 else 'weak'} relationship—premium districts sometimes offer higher yields.")

st.divider()

# ===== OPERATING COSTS COMPARISON =====
section_intro("Cost Efficiency Analysis", "Service charges and maintenance costs impact net investor returns.")
c1, c2 = st.columns(2)

with c1:
    fig = px.bar(g.sort_values("service_charge_median"), 
                 x=g.sort_values("service_charge_median").index, 
                 y="service_charge_median", 
                 title="Annual Service Charge by District")
    fig.update_layout(xaxis_title="District", yaxis_title="AED/sqm/year")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    cost_range = ((g['service_charge_median'].max() - g['service_charge_median'].min()) / g['service_charge_median'].mean())
    takeaway(f"Cost variance spans ±{cost_range:.0%} of mean, suggesting different asset maintenance standards across markets.")

with c2:
    g_temp = g.copy()
    g_temp['cost_to_yield'] = (g_temp['service_charge_median'] / (g_temp['net_yield_median'] * g_temp['median_price_sqm'] / 100)).fillna(0)
    fig = px.bar(g_temp.sort_values("cost_to_yield"), 
                 x=g_temp.sort_values("cost_to_yield").index, 
                 y="cost_to_yield", 
                 title="Cost Burden (Service Charge / Annual Yield)")
    fig.update_layout(xaxis_title="District", yaxis_title="Cost Ratio")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
    takeaway("Ratio indicates what % of annual yield is consumed by operating costs. Lower ratios = less friction on returns.")

st.divider()

# ===== PRODUCT MIX COMPARISON =====
section_intro("Product Type Pricing", "How different property types (bedrooms) command premia across districts.")
if "bedrooms" in view.columns and "price_per_sqm" in view.columns:
    d = view.dropna(subset=["district", "bedrooms", "price_per_sqm"]).copy()
    if len(d) >= 30:
        pivot = (
            d.groupby(["district", "bedrooms"])["price_per_sqm"]
            .median()
            .reset_index()
            .rename(columns={"price_per_sqm": "median_price_sqm"})
        )
        fig = px.line(
            pivot,
            x="bedrooms",
            y="median_price_sqm",
            color="district",
            markers=True,
            title="Price Curve by Product Type (Median AED/sqm)",
        )
        fig.update_layout(xaxis_title="Bedrooms", yaxis_title="Median AED per sqm")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
        
        # Identify steepest price curve (most differentiation by type)
        slopes = {}
        for dist in pivot['district'].unique():
            dist_data = pivot[pivot['district'] == dist].sort_values('bedrooms')
            if len(dist_data) >= 2:
                slope = (dist_data.iloc[-1]['median_price_sqm'] - dist_data.iloc[0]['median_price_sqm'])
                slopes[dist] = slope
        if slopes:
            most_differentiated = max(slopes, key=slopes.get)
            takeaway(f"{most_differentiated} shows steepest price-by-type curve, indicating strong buyer segmentation by product size.")
    else:
        st.info("Insufficient typology data for product mix analysis.")
