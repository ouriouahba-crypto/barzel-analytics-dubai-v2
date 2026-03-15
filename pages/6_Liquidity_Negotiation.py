import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme, section_intro, chart_explanation
from src.app.translations import get_text

lang = st.session_state.get("language", "en")

hero(get_text("liquidity_title", lang), get_text("liquidity_subtitle", lang))

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

need = ["days_on_market", "price_per_sqm"]
missing = [c for c in need if c not in view.columns]
if missing:
    st.error(f"Missing columns for liquidity analysis: {missing}")
    st.stop()

d = view.dropna(subset=["days_on_market"]).copy()

# Cards
c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card(get_text("kpi_listings", lang), f"{len(view):,}", get_text("non_null_share", lang))
with c2: kpi_card(get_text("kpi_dom_coverage", lang), f"{view['days_on_market'].notna().mean():.0%}", get_text("non_null_share", lang))
with c3: kpi_card(get_text("kpi_median_dom", lang), f"{int(d['days_on_market'].median()):,}" if len(d) else "n/a", get_text("exit_speed", lang))
with c4: kpi_card(get_text("kpi_fast_sale_30", lang), f"{(d['days_on_market'] <= 30).mean():.0%}" if len(d) else "n/a", get_text("liquidity_signal", lang))

st.divider()

# DOM distribution
section_intro(get_text("section_time_exit_distribution", lang), get_text("section_time_exit_absorption", lang))
chart_explanation(get_text("exit_distribution_explanation", lang))
fig = px.histogram(d, x="days_on_market", nbins=45, title=get_text("chart_days_market", lang))
fig.update_layout(xaxis_title="Days on Market", yaxis_title="Listing Count")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

# Price vs DOM scatter
section_intro(get_text("section_pricing_discipline_title", lang), get_text("section_pricing_discipline_sub", lang))
chart_explanation(get_text("pricing_discipline_micro", lang))
s = view.dropna(subset=["price_per_sqm", "days_on_market"]).copy()
if len(s) >= 40:
    fig = px.scatter(
        s,
        x="price_per_sqm",
        y="days_on_market",
        color="district" if "district" in s.columns else None,
        opacity=0.55,
        title=get_text("chart_price_exit", lang),
        hover_data=[c for c in ["building_name", "bedrooms", "size_sqm"] if c in s.columns],
    )
    fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Days on Market")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

# Fast-sale table by district
if "district" in view.columns:
    section_intro(get_text("section_district_liquidity_title", lang), get_text("section_district_liquidity_sub", lang))
    t = view.dropna(subset=["days_on_market"]).groupby("district")["days_on_market"].agg(
        n="count",
        median="median",
        fast_30=lambda x: (x <= 30).mean(),
        fast_60=lambda x: (x <= 60).mean(),
    ).reset_index()
    st.dataframe(t.sort_values("n", ascending=False), use_container_width=True)
