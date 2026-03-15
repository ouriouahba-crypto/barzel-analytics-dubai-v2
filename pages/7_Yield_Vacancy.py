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
sel = st.multiselect(get_text("label_districts", lang), districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

if "net_yield" not in view.columns:
    st.error("Missing net_yield column (facts mapping not applied).")
    st.stop()

d = view.dropna(subset=["net_yield"]).copy()

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card(get_text("kpi_listings", lang), f"{len(view):,}", get_text("selection_size", lang))
with c2: kpi_card(get_text("kpi_yield_coverage", lang), f"{view['net_yield'].notna().mean():.0%}", get_text("non_null_share", lang))
with c3: kpi_card(get_text("kpi_median_yield", lang), f"{d['net_yield'].median():.2f}%" if len(d) else "n/a", get_text("central_yield", lang))
with c4: kpi_card(get_text("kpi_p90_yield", lang), f"{d['net_yield'].quantile(0.9):.2f}%" if len(d) else "n/a", get_text("upper_yield", lang))

st.divider()

section_intro(get_text("section_yield_distribution", lang), get_text("yield_distr_sub", lang))
chart_explanation(get_text("yield_dist_explanation", lang))
fig = px.histogram(d, x="net_yield", nbins=35, title=get_text("chart_yield_distribution", lang))
fig.update_layout(xaxis_title="Net yield (%)", yaxis_title="Listing Count")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

if "price_per_sqm" in view.columns:
    section_intro(get_text("section_price_yield_analysis", lang), get_text("price_yield_sub", lang))
    chart_explanation(get_text("price_yield_explanation", lang))
    s = view.dropna(subset=["price_per_sqm", "net_yield"]).copy()
    if len(s) >= 40:
        fig = px.scatter(
            s,
            x="price_per_sqm",
            y="net_yield",
            color="district" if "district" in s.columns else None,
            opacity=0.55,
            title=get_text("chart_price_yield_tradeoff", lang),
        )
        fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Net yield (%)")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

# Vacancy (if present)
if "vacancy_days" in view.columns:
    st.divider()
    section_intro(get_text("section_vacancy_analysis", lang), get_text("vacancy_sub", lang))
    chart_explanation(get_text("vacancy_explanation", lang))
    v = view.dropna(subset=["vacancy_days"]).copy()
    if len(v) >= 30:
        fig = px.histogram(v, x="vacancy_days", nbins=35, title=get_text("chart_vacancy_days", lang))
        fig.update_layout(xaxis_title="Vacancy days", yaxis_title="Listing Count")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
