import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme
from src.analytics.market_views import snapshots_by


hero("Compare", "Cross-district comparison. Descriptive only (no score).")

df = st.session_state.get("df")
if df is None or df.empty or "district" not in df.columns:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist())
sel = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

g = snapshots_by(view, "district")
if g.empty:
    st.info("Not enough data for comparison.")
    st.stop()

# Top cards
c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Districts", f"{len(g):,}", "Selection")
with c2: kpi_card("Total listings", f"{int(g['n_obs'].sum()):,}", "Across selection")
with c3: kpi_card("Best median AED/sqm", f"{int(g['median_price_sqm'].min()):,}", "Cheapest median")
with c4: kpi_card("Fastest median DOM", f"{int(g['median_dom'].min()):,}", "Fastest exit")

st.subheader("District table")
st.dataframe(g.sort_values("n_obs", ascending=False), use_container_width=True)

st.divider()

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(g, x="district", y="median_price_sqm", title="Median AED/sqm by district")
    fig.update_layout(xaxis_title="District", yaxis_title="Median AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

with c2:
    fig = px.bar(g, x="district", y="median_dom", title="Median Days on Market by district")
    fig.update_layout(xaxis_title="District", yaxis_title="Median Days on Market")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

c3, c4 = st.columns(2)
with c3:
    fig = px.bar(g, x="district", y="net_yield_median", title="Net Yield (median) by district")
    fig.update_layout(xaxis_title="District", yaxis_title="Net yield (median, %)")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

with c4:
    fig = px.bar(g, x="district", y="service_charge_median", title="Service charge (median) by district")
    fig.update_layout(xaxis_title="District", yaxis_title="Service charge (AED/sqm/year, median)")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

fig = px.bar(g, x="district", y="overpricing_penalty_corr", title="Overpricing penalty (corr price vs DOM)")
fig.update_layout(xaxis_title="District", yaxis_title="Correlation (price vs DOM)")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

# Drilldown: typology (if available)
if "bedrooms" in view.columns and "price_per_sqm" in view.columns:
    st.divider()
    st.subheader("Drilldown: Median AED/sqm by district & bedrooms")
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
            title="Median AED/sqm vs Bedrooms (by district)",
        )
        fig.update_layout(xaxis_title="Bedrooms", yaxis_title="Median AED per sqm")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
