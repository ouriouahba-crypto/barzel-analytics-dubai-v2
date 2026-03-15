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
sel = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

col = "service_charge_psm_year"
if col not in view.columns:
    st.error("Missing service_charge_psm_year column (facts mapping not applied).")
    st.stop()

d = view.dropna(subset=[col]).copy()

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Listings", f"{len(view):,}", "Selection size")
with c2: kpi_card("Charges coverage", f"{view[col].notna().mean():.0%}", "Non-null share")
with c3: kpi_card("Median charges", f"{int(d[col].median()):,}" if len(d) else "n/a", "AED/sqm/year")
with c4: kpi_card("P90 charges", f"{int(d[col].quantile(0.9)):,}" if len(d) else "n/a", "Upper tail")

st.divider()

section_intro("Operating Cost Distribution", "Understanding service charge variability.")
chart_explanation("This histogram shows the distribution of annual service charges across properties. Properties clustering to the left have lower operating costs; those on the right are more expensive to maintain. Outliers may indicate luxury amenities or aging infrastructure requiring higher maintenance investment.")
fig = px.histogram(d, x=col, nbins=35, title="Service Charge Distribution")
fig.update_layout(xaxis_title="AED per sqm per year", yaxis_title="Listing Count")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

if "district" in d.columns:
    section_intro("Cost Benchmarking by District", "Comparative operating expenses across markets.")
    chart_explanation("This bar chart ranks districts by median service charges. Higher costs may reflect newer construction, premium amenities, or higher-spec maintenance standards. Lower costs may signal value opportunities, but verify that assets are not under-maintained.")
    g = d.groupby("district")[col].median().reset_index().sort_values(col)
    fig = px.bar(g, x="district", y=col, title="Median Service Charges by District")
    fig.update_layout(xaxis_title="District", yaxis_title="Median AED per sqm per year")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

if "net_yield" in d.columns:
    st.divider()
    section_intro("Cost Impact on Yield", "Relationship between operational expenses and net returns.")
    chart_explanation("This scatter plot reveals how service charges affect net yield. Properties in the upper-left quadrant offer low costs and strong returns — an ideal investment profile. Lower-right properties have high costs eating into returns.")
    s = d.dropna(subset=["net_yield"]).copy()
    if len(s) >= 40:
        fig = px.scatter(s, x=col, y="net_yield", color="district" if "district" in s.columns else None,
                         opacity=0.55, title="Cost Burden vs. Net Yield")
        fig.update_layout(xaxis_title="AED per sqm per year", yaxis_title="Net yield (%)")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
