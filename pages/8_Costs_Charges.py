import streamlit as st
import plotly.express as px

from src.app.ui import (
    hero, kpi_card, selection_bar, apply_plotly_theme,
    section_intro, chart_explanation, premium_insight, narrative_text
)
from src.app.translations import get_text

lang = st.session_state.get("language", "en")

hero("Costs Charges", "Charges, friction and cost pressure (descriptive only).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = selection_bar(districts, label="Districts", default=districts[:3] if len(districts) >= 3 else districts)
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
chart_explanation(get_text("operating_explanation", lang))
fig = px.histogram(d, x=col, nbins=35, title="Service Charge Distribution")
fig.update_layout(xaxis_title="AED per sqm per year", yaxis_title="Listing Count")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
premium_insight(
    narrative_text(
        "Charge dispersion helps separate efficient operating stock from buildings where expenses may materially erode investor returns.",
        "La dispersion des charges permet de distinguer les actifs operationnellement efficaces des immeubles ou les depenses peuvent rogner sensiblement le rendement investisseur.",
    ),
    "🏗️",
)

st.divider()

if "district" in d.columns:
    section_intro("Cost Benchmark by District", "Median service-charge levels across selected districts.")
    chart_explanation(get_text("bench_explanation", lang))
    g = d.groupby("district")[col].median().reset_index().sort_values(col)
    fig = px.bar(g, x="district", y=col, title="Median Service Charge by District")
    fig.update_layout(xaxis_title="District", yaxis_title="Median AED per sqm per year")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
    premium_insight(
        narrative_text(
            "District benchmarking shows whether cost pressure is structural to the location or concentrated in specific assets.",
            "Le benchmarking par district permet de voir si la pression sur les charges est structurelle a la localisation ou concentree sur certains actifs.",
        ),
        "📊",
    )

if "net_yield" in d.columns:
    st.divider()
    section_intro("Cost Impact on Yield", "Relationship between operational expenses and net returns.")
    chart_explanation(get_text("cost_yield_explanation", lang))
    s = d.dropna(subset=["net_yield"]).copy()
    if len(s) >= 40:
        fig = px.scatter(s, x=col, y="net_yield", color="district" if "district" in s.columns else None,
                         opacity=0.55, title="Cost Burden vs. Net Yield")
        fig.update_layout(xaxis_title="AED per sqm per year", yaxis_title="Net yield (%)")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
        premium_insight(
            narrative_text(
                "The most attractive zone remains low-cost stock with resilient yield, while high-cost low-yield assets deserve closer underwriting scrutiny.",
                "La zone la plus attractive reste celle des actifs a faibles charges et rendement resilient, tandis que les actifs couteux et peu rentables meritent un underwriting plus prudent.",
            ),
            "💼",
        )
