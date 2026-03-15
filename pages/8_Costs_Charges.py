import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme, section_intro, chart_explanation
from src.app.translations import get_text

lang = st.session_state.get("language", "en")

hero(get_text("costs_title", lang), get_text("costs_subtitle", lang))

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = st.multiselect(get_text("label_districts", lang), districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

col = "service_charge_psm_year"
if col not in view.columns:
    st.error("Missing service_charge_psm_year column (facts mapping not applied).")
    st.stop()

d = view.dropna(subset=[col]).copy()

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card(get_text("kpi_listings", lang), f"{len(view):,}", get_text("selection_size", lang))
with c2: kpi_card(get_text("kpi_charges_coverage", lang), f"{view[col].notna().mean():.0%}", get_text("non_null_share", lang))
with c3: kpi_card(get_text("kpi_median_charges", lang), f"{int(d[col].median()):,}" if len(d) else "n/a", get_text("aed_sqm_year", lang))
with c4: kpi_card(get_text("kpi_p90_charges", lang), f"{int(d[col].quantile(0.9)):,}" if len(d) else "n/a", get_text("upper_tail", lang))

st.divider()

section_intro(get_text("section_operating_dist", lang), get_text("operating_dist_sub", lang))
chart_explanation(get_text("operating_explanation", lang))
fig = px.histogram(d, x=col, nbins=35, title=get_text("chart_service_distribution", lang))
fig.update_layout(xaxis_title="AED per sqm per year", yaxis_title="Listing Count")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

if "district" in d.columns:
    section_intro(get_text("section_cost_benchmark", lang), get_text("cost_bench_sub", lang))
    chart_explanation(get_text("bench_explanation", lang))
    g = d.groupby("district")[col].median().reset_index().sort_values(col)
    fig = px.bar(g, x="district", y=col, title=get_text("chart_median_charges", lang))
    fig.update_layout(xaxis_title="District", yaxis_title="Median AED per sqm per year")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

if "net_yield" in d.columns:
    st.divider()
    section_intro(get_text("section_cost_yield_impact", lang), get_text("cost_yield_sub", lang))
    chart_explanation(get_text("cost_yield_explanation", lang))
    s = d.dropna(subset=["net_yield"]).copy()
    if len(s) >= 40:
        fig = px.scatter(s, x=col, y="net_yield", color="district" if "district" in s.columns else None,
                         opacity=0.55, title=get_text("chart_cost_burden_yield", lang))
        fig.update_layout(xaxis_title="AED per sqm per year", yaxis_title="Net yield (%)")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
