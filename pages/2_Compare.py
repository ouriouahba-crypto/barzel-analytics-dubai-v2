import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.app.ui import (
    hero, kpi_card, selection_bar, apply_plotly_theme,
    section_intro, takeaway, chart_explanation, premium_insight,
    executive_summary, narrative_text
)
from src.app.translations import get_text
from src.analytics.market_views import snapshots_by

lang = st.session_state.get("language", "en")

hero(get_text("compare_title", lang), get_text("compare_subtitle", lang))

df = st.session_state.get("df")
if df is None or df.empty or "district" not in df.columns:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist())
sel = selection_bar(
    districts,
    label=get_text("label_districts", lang),
    default=districts[:3] if len(districts) >= 3 else districts
)
view = df[df["district"].isin(sel)] if sel else df

g = snapshots_by(view, "district")
if g.empty:
    st.info("Not enough data for comparison.")
    st.stop()

g = g.copy()
g["district"] = g["district"].astype(str)

# ===== COMPARATIVE SUMMARY =====
section_intro(
    get_text("compare_intro_title", lang),
    get_text("compare_intro_subtitle", lang)
)

most_expensive = g.loc[g["median_price_sqm"].idxmax()]
most_affordable = g.loc[g["median_price_sqm"].idxmin()]
most_liquid = g.loc[g["median_dom"].idxmin()]
best_yields = g.loc[g["net_yield_median"].idxmax()]
lowest_costs = g.loc[g["service_charge_median"].idxmin()]
slowest_liquidity = g.loc[g["median_dom"].idxmax()]

summary_points = [
    narrative_text(
        f"Pricing ranges from {int(most_affordable['median_price_sqm']):,} AED/sqm ({most_affordable['district']}) to {int(most_expensive['median_price_sqm']):,} AED/sqm ({most_expensive['district']}), reflecting {((most_expensive['median_price_sqm'] / most_affordable['median_price_sqm'] - 1) * 100):.0f}% market segmentation.",
        f"Le pricing s'etend de {int(most_affordable['median_price_sqm']):,} AED/sqm ({most_affordable['district']}) a {int(most_expensive['median_price_sqm']):,} AED/sqm ({most_expensive['district']}), soit environ {((most_expensive['median_price_sqm'] / most_affordable['median_price_sqm'] - 1) * 100):.0f}% d'ecart entre les deux extremes.",
    ),
    narrative_text(
        f"Most liquid market: {most_liquid['district']} exits in median {int(most_liquid['median_dom'])} days. Slowest: {slowest_liquidity['district']} ({int(slowest_liquidity['median_dom'])} days).",
        f"Le marche le plus liquide est {most_liquid['district']} avec une sortie mediane en {int(most_liquid['median_dom'])} jours, contre {slowest_liquidity['district']} a {int(slowest_liquidity['median_dom'])} jours.",
    ),
    narrative_text(
        f"Yield spreads across districts: {best_yields['district']} leads at {best_yields['net_yield_median']:.2f}% versus a low of {g['net_yield_median'].min():.2f}%.",
        f"Les rendements restent disperses : {best_yields['district']} mene a {best_yields['net_yield_median']:.2f}% contre un point bas a {g['net_yield_median'].min():.2f}%.",
    ),
    narrative_text(
        f"Operating cost efficiency varies materially: {lowest_costs['district']} charges {int(lowest_costs['service_charge_median']):,} AED/sqm/yr versus {int(g['service_charge_median'].max()):,} in the highest-cost district.",
        f"L'efficacite des charges varie nettement : {lowest_costs['district']} se situe a {int(lowest_costs['service_charge_median']):,} AED/sqm/yr contre {int(g['service_charge_median'].max()):,} dans le district le plus couteux.",
    ),
]

executive_summary(summary_points[:3])

st.divider()

# ===== TOP KPIS =====
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Districts Compared", f"{len(g):,}", "In selection")
with c2:
    kpi_card("Total Market Size", f"{int(g['n_obs'].sum()):,}", "Active listings")
with c3:
    kpi_card(
        "Price Premium Spread",
        f"{((most_expensive['median_price_sqm'] / most_affordable['median_price_sqm']) - 1):.0%}",
        "High vs Low"
    )
with c4:
    kpi_card(
        "Liquidity Range",
        f"{int(g['median_dom'].max() - g['median_dom'].min())} days",
        "Max - Min DOM"
    )

st.divider()

# ===== DISTRICT SUMMARY TABLE =====
section_intro("Complete District Benchmarking", "All metrics for comparative analysis.")

table_sorted = g.sort_values("n_obs", ascending=False)
display_cols = {
    "district": "District",
    "n_obs": "Listings",
    "median_price_sqm": "Median Price (AED/sqm)",
    "median_dom": "Median DOM (days)",
    "net_yield_median": "Median Yield (%)",
    "service_charge_median": "Service Charge (AED/sqm/yr)",
    "fast_sale_ratio_30d": "Quick Sales ≤30d (%)",
    "price_consistency_cv": "Price Variation (CV)",
}

display_table = table_sorted[[col for col in display_cols.keys() if col in table_sorted.columns]].copy()
display_table.columns = [display_cols.get(col, col) for col in display_table.columns]

for col in display_table.columns:
    if "AED" in col or "Price" in col or "Service" in col:
        display_table[col] = display_table[col].apply(
            lambda x: f"{x:,.0f}" if pd.notna(x) else "n/a"
        )
    elif "%" in col or "Yield" in col or "Quick" in col:
        if "Yield" in col:
            display_table[col] = display_table[col].apply(
                lambda x: f"{x:.2f}" if pd.notna(x) else "n/a"
            )
        else:
            display_table[col] = display_table[col].apply(
                lambda x: f"{x:.1%}" if pd.notna(x) else "n/a"
            )
    elif "CV" in col or "Variation" in col:
        display_table[col] = display_table[col].apply(
            lambda x: f"{x:.3f}" if pd.notna(x) else "n/a"
        )
    elif "DOM" in col:
        display_table[col] = display_table[col].apply(
            lambda x: f"{int(x)}" if pd.notna(x) else "n/a"
        )

st.dataframe(display_table, use_container_width=True)

st.divider()

# ===== PRICING COMPARISON =====
section_intro("Pricing Landscape", "Median AED/sqm across districts reveals market segmentation.")
chart_explanation(get_text("pricing_chart_explanation", lang))
c1, c2 = st.columns(2)

with c1:
    sorted_price = g.sort_values("median_price_sqm", ascending=False).copy()

    fig = px.bar(
        sorted_price,
        x="district",
        y="median_price_sqm",
        title="Median Price by District (Ranked)"
    )
    fig.update_layout(xaxis_title="District", yaxis_title="Median AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

    price_spread = (g["median_price_sqm"].max() - g["median_price_sqm"].min()) / g["median_price_sqm"].mean()
    market_structure = "distinct market segments with clear tier stratification" if price_spread > 0.20 else "relatively homogeneous pricing across districts"
    premium_insight(
        narrative_text(
            f"Market structure: Price variance of ±{price_spread:.0%} indicates {market_structure}.",
            f"Un ecart de prix de ±{price_spread:.0%} confirme {('des segments de marche bien differencies' if price_spread > 0.20 else 'une structure de prix relativement homogene entre districts')}.",
        ),
        "📊",
    )

with c2:
    box_df = view.dropna(subset=["district", "price_per_sqm"]).copy()
    fig = px.box(
        box_df,
        x="district",
        y="price_per_sqm",
        title="Pricing Distribution by District"
    )
    fig.update_layout(xaxis_title="District", yaxis_title="AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

    district_std_mean = box_df.groupby("district")["price_per_sqm"].std().mean()
    discipline = "tight pricing discipline with minimal outliers" if district_std_mean < 500 else "significant price heterogeneity suggesting diverse product mix or quality variance"
    premium_insight(
        narrative_text(
            f"Price discipline: Districts show {discipline}.",
            f"Les districts montrent {('une discipline de prix plutot serree' if district_std_mean < 500 else 'une heterogeneite de prix marquee, probablement liee au mix produit ou a la qualite des actifs')}.",
        ),
        "🎯",
    )

st.divider()

# ===== LIQUIDITY COMPARISON =====
section_intro("Market Liquidity & Exit Dynamics", "Days-on-market reveals relative market depth and absorption capacity.")
chart_explanation(get_text("liquidity_chart_explanation", lang))
c1, c2 = st.columns(2)

with c1:
    sorted_dom = g.sort_values("median_dom").copy()

    fig = px.bar(
        sorted_dom,
        x="district",
        y="median_dom",
        title="Median Time-to-Exit by District"
    )
    fig.update_layout(xaxis_title="District", yaxis_title="Days on Market")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

    fastest = g["median_dom"].min()
    slowest = g["median_dom"].max()
    liquidity_delta = int(slowest - fastest)
    premium_insight(
        narrative_text(
            f"Liquidity variance: {liquidity_delta}-day range between most ({int(fastest)}d) and least liquid ({int(slowest)}d) markets.",
            f"L'ecart de liquidite atteint {liquidity_delta} jours entre le marche le plus rapide ({int(fastest)}j) et le plus lent ({int(slowest)}j).",
        ),
        "⚡",
    )

with c2:
    sorted_fast_sales = g.sort_values("fast_sale_ratio_30d", ascending=False).copy()

    fig = px.bar(
        sorted_fast_sales,
        x="district",
        y="fast_sale_ratio_30d",
        title="Quick Sales (≤30 days) by District"
    )
    fig.update_layout(xaxis_title="District", yaxis_title="% of Units")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

    avg_quick_ratio = g["fast_sale_ratio_30d"].mean()
    momentum = "strong buyer momentum and efficient absorption" if avg_quick_ratio > 0.25 else "moderate market pull with selective demand"
    premium_insight(
        narrative_text(
            f"Quick-sale dynamics: {avg_quick_ratio:.0%} portfolio average indicates {momentum}.",
            f"En moyenne, {avg_quick_ratio:.0%} du portefeuille se vend en moins de 30 jours, ce qui traduit {('une traction acheteuse forte' if avg_quick_ratio > 0.25 else 'une demande plus selective')}.",
        ),
        "📈",
    )

st.divider()

# ===== YIELD COMPARISON =====
section_intro("Income Return Profile", "Net yields reflect rental market dynamics relative to acquisition prices.")
chart_explanation(get_text("yield_chart_explanation", lang))
c1, c2 = st.columns(2)

with c1:
    sorted_yield = g.sort_values("net_yield_median", ascending=False).copy()

    fig = px.bar(
        sorted_yield,
        x="district",
        y="net_yield_median",
        title="Median Net Yield by District"
    )
    fig.update_layout(xaxis_title="District", yaxis_title="Net Yield (%)")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

    yield_range = g["net_yield_median"].max() - g["net_yield_median"].min()
    yield_spread = yield_range / g["net_yield_median"].mean()
    premium_insight(
        narrative_text(
            f"Yield dispersion: {yield_range:.2f}% absolute range (±{yield_spread:.0%} relative) across districts indicates differentiated income dynamics.",
            f"Un spread de rendement de {yield_range:.2f}% (±{yield_spread:.0%} relatif) signale des dynamiques de revenu distinctes selon les districts.",
        ),
        "💰",
    )

with c2:
    scatter_df = g.copy()

    scatter_cols = ["district", "median_price_sqm", "net_yield_median"]
    if "n_obs" in scatter_df.columns:
        scatter_cols.append("n_obs")

    scatter_df = scatter_df[scatter_cols].copy()
    scatter_df = scatter_df.dropna(subset=["median_price_sqm", "net_yield_median"]).reset_index(drop=True)

    if "n_obs" in scatter_df.columns:
        marker_sizes = scatter_df["n_obs"].fillna(1).astype(float).tolist()
    else:
        marker_sizes = [12.0] * len(scatter_df)

    sizeref = max(marker_sizes) / 40 if marker_sizes and max(marker_sizes) > 0 else 1

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=scatter_df["median_price_sqm"].astype(float).tolist(),
            y=scatter_df["net_yield_median"].astype(float).tolist(),
            mode="markers+text",
            text=scatter_df["district"].tolist(),
            textposition="top center",
            hovertext=scatter_df["district"].tolist(),
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Median Price: %{x:,.0f} AED/sqm<br>"
                "Net Yield: %{y:.2f}%<extra></extra>"
            ),
            marker=dict(
                size=marker_sizes,
                sizemode="area",
                sizeref=sizeref,
                sizemin=8,
            ),
            name="Districts",
        )
    )

    fig.update_layout(
        title="Price vs. Yield Trade-off",
        xaxis_title="Median Price (AED/sqm)",
        yaxis_title="Net Yield (%)",
    )

    st.plotly_chart(
        apply_plotly_theme(fig),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    corr_price_yield = g["median_price_sqm"].corr(g["net_yield_median"])
    if corr_price_yield < -0.3:
        insight = "strong inverse relationship — premium pricing typically commands lower yields"
    elif corr_price_yield > 0.2:
        insight = "positive relationship — higher-priced districts also offer better returns"
    else:
        insight = "weak or no relationship — price and yield move independently"
    premium_insight(
        narrative_text(
            f"Price-yield dynamics: {corr_price_yield:+.2f} correlation signals {insight}.",
            f"La correlation de {corr_price_yield:+.2f} suggere {('une relation inverse marquee entre prix et rendement' if corr_price_yield < -0.3 else 'une relation positive entre prix et rendement' if corr_price_yield > 0.2 else 'une relation faible entre prix et rendement')}.",
        ),
        "🔗",
    )

st.divider()

# ===== OPERATING COSTS COMPARISON =====
section_intro("Cost Efficiency Analysis", "Service charges and maintenance costs impact net investor returns.")
chart_explanation(get_text("costs_chart_explanation", lang))
c1, c2 = st.columns(2)

with c1:
    sorted_costs = g.sort_values("service_charge_median").copy()

    fig = px.bar(
        sorted_costs,
        x="district",
        y="service_charge_median",
        title="Annual Service Charge by District"
    )
    fig.update_layout(xaxis_title="District", yaxis_title="AED/sqm/year")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

    cost_range = (g["service_charge_median"].max() - g["service_charge_median"].min()) / g["service_charge_median"].mean()
    premium_insight(
        narrative_text(
            f"Cost variance: ±{cost_range:.0%} of mean indicates different asset maintenance standards and building age profiles across districts.",
            f"Un ecart de cout de ±{cost_range:.0%} autour de la moyenne suggere des standards d'entretien et des ages de parc differents entre districts.",
        ),
        "🏗️",
    )

with c2:
    g_temp = g.copy()
    g_temp["cost_to_yield"] = (
        g_temp["service_charge_median"] /
        (g_temp["net_yield_median"] * g_temp["median_price_sqm"] / 100)
    ).fillna(0)

    sorted_burden = g_temp.sort_values("cost_to_yield")

    fig = px.bar(
        sorted_burden,
        x="district",
        y="cost_to_yield",
        title="Cost Burden (Service Charge / Annual Yield)"
    )
    fig.update_layout(xaxis_title="District", yaxis_title="Cost Ratio")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

    premium_insight(
        narrative_text(
            "The cost-to-yield ratio shows what fraction of annual rental income is consumed by operating costs. Lower ratios preserve more cash flow for investors.",
            "Le ratio charge-rendement mesure la part du revenu locatif annuel absorbee par les couts d'exploitation. Plus il est bas, plus le cash-flow investisseur est preserve.",
        ),
        "💼",
    )

st.divider()

# ===== PRODUCT MIX COMPARISON =====
section_intro("Product Type Pricing", "How different property types (bedrooms) command premia across districts.")
chart_explanation(narrative_text(
    "This line chart shows how median pricing varies by bedroom count across your selected districts. Steeper slopes indicate stronger buyer segmentation by product size.",
    "Ce graphique montre comment le prix median evolue selon le nombre de chambres dans les districts selectionnes. Des pentes plus marquees signalent une segmentation produit plus forte.",
))
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

        slopes = {}
        for dist in pivot["district"].unique():
            dist_data = pivot[pivot["district"] == dist].sort_values("bedrooms")
            if len(dist_data) >= 2:
                slope = dist_data.iloc[-1]["median_price_sqm"] - dist_data.iloc[0]["median_price_sqm"]
                slopes[dist] = slope

        if slopes:
            most_differentiated = max(slopes, key=slopes.get)
            least_differentiated = min(slopes, key=slopes.get)
            avg_slope = sum(slopes.values()) / len(slopes) if slopes else 0
            premium_insight(
                narrative_text(
                    f"Product segmentation: {most_differentiated} shows steepest price-by-type curve, suggesting strongest buyer differentiation. Flatter curves indicate commodity pricing.",
                    f"{most_differentiated} presente la courbe prix-produit la plus pentue, ce qui signale la segmentation acheteur la plus marquee. Des courbes plus plates renvoient a un pricing plus commoditise.",
                ),
                "📏",
            )
    else:
        st.info("Insufficient typology data for product mix analysis.")
