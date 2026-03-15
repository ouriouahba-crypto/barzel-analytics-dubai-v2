import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme, section_intro, chart_explanation
from src.app.translations import get_text

lang = st.session_state.get("language", "en")

hero(get_text("yield_title", lang), get_text("yield_subtitle", lang))

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

if "net_yield" not in view.columns:
    st.error("Missing net_yield column (facts mapping not applied).")
    st.stop()

d = view.dropna(subset=["net_yield"]).copy()

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Listings", f"{len(view):,}", "Selection size")
with c2: kpi_card("Yield coverage", f"{view['net_yield'].notna().mean():.0%}", "Non-null share")
with c3: kpi_card("Median net yield", f"{d['net_yield'].median():.2f}%" if len(d) else "n/a", "Central yield")
with c4: kpi_card("P90 net yield", f"{d['net_yield'].quantile(0.9):.2f}%" if len(d) else "n/a", "Upper yield")

st.divider()

section_intro("Income Yield Distribution", "Understanding rental return variability across properties.")
chart_explanation("This histogram displays the distribution of net yields across your portfolio. Left-skewed distributions indicate concentrated high-yield properties, while right-skewed patterns show more competitive moderate-yield assets.")
fig = px.histogram(d, x="net_yield", nbins=35, title="Net Yield Distribution")
fig.update_layout(xaxis_title="Net yield (%)", yaxis_title="Listing Count")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

if "price_per_sqm" in view.columns:
    section_intro("Price-Yield Tradeoff Analysis", "Relationship between acquisition cost and income return.")
    chart_explanation("This scatter plot reveals the price-yield relationship. Typically, premium-priced properties (upper-right quadrant) have lower yields, while value properties (lower-left) often yield more. This chart identifies compelling value propositions and potential bargains.")
    s = view.dropna(subset=["price_per_sqm", "net_yield"]).copy()
    if len(s) >= 40:
        fig = px.scatter(
            s,
            x="price_per_sqm",
            y="net_yield",
            color="district" if "district" in s.columns else None,
            opacity=0.55,
            title="Price vs. Yield Trade-off",
        )
        fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Net yield (%)")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

# Vacancy (if present)
if "vacancy_days" in view.columns:
    st.divider()
    section_intro("Vacancy Duration Analysis", "Understanding absorption patterns for vacant units.")
    chart_explanation("This histogram shows how long vacant units remain unoccupied. Properties clustering on the left indicate quick re-leasing, while properties on the right suggest challenging market absorption.")
    v = view.dropna(subset=["vacancy_days"]).copy()
    if len(v) >= 30:
        fig = px.histogram(v, x="vacancy_days", nbins=35, title="Vacancy Days Distribution")
        fig.update_layout(xaxis_title="Vacancy days", yaxis_title="Listing Count")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
