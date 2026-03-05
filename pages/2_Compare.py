import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, selection_bar, apply_plotly_theme
from src.analytics.market_views import snapshots_by


hero("Compare", "Side-by-side district analysis across key metrics.")

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

# Top cards
c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Districts", f"{len(g):,}", "In selection")
with c2: kpi_card("Total Listings", f"{int(g['n_obs'].sum()):,}", "Across selection")
with c3: kpi_card("Most Affordable", f"{int(g['median_price_sqm'].min()):,} AED/sqm", "Lowest median")
with c4: kpi_card("Fastest Exit", f"{int(g['median_dom'].min()):,} days", "Quickest DOM")

st.markdown("")

st.subheader("District Summary")
st.dataframe(g.sort_values("n_obs", ascending=False), use_container_width=True)

st.markdown("")

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(g, x="district", y="median_price_sqm", title="Pricing Comparison")
    fig.update_layout(xaxis_title="District", yaxis_title="Median AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

with c2:
    fig = px.bar(g, x="district", y="median_dom", title="Liquidity Comparison")
    fig.update_layout(xaxis_title="District", yaxis_title="Median Days on Market")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

st.markdown("")

c3, c4 = st.columns(2)
with c3:
    fig = px.bar(g, x="district", y="net_yield_median", title="Yield Comparison")
    fig.update_layout(xaxis_title="District", yaxis_title="Net Yield (%)")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

with c4:
    fig = px.bar(g, x="district", y="service_charge_median", title="Operating Costs")
    fig.update_layout(xaxis_title="District", yaxis_title="Annual Service Charge (AED/sqm)")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

st.markdown("")

fig = px.bar(g, x="district", y="overpricing_penalty_corr", title="Price-Time Discipline")
fig.update_layout(xaxis_title="District", yaxis_title="Price/DOM Correlation")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})

# Drilldown: typology (if available)
if "bedrooms" in view.columns and "price_per_sqm" in view.columns:
    st.markdown("")
    st.subheader("Product Type Pricing")
    d = view.dropna(subset=["district", "bedrooms", "price_per_sqm"]).copy()
    if len(d) >= 50:
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
            title="Price Curve by Product Type",
        )
        fig.update_layout(xaxis_title="Bedrooms", yaxis_title="Median AED per sqm")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True, config={"displayModeBar": False})
