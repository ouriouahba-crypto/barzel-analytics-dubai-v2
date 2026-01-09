import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme


hero("Costs", "Charges, friction and cost pressure (descriptive only).")

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

fig = px.histogram(d, x=col, nbins=35, title="Distribution: service charges (AED/sqm/year)")
fig.update_layout(xaxis_title="AED / sqm / year", yaxis_title="Count")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

if "district" in d.columns:
    g = d.groupby("district")[col].median().reset_index().sort_values(col)
    fig = px.bar(g, x="district", y=col, title="Median service charges by district")
    fig.update_layout(xaxis_title="District", yaxis_title="Median AED / sqm / year")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

if "net_yield" in d.columns:
    st.divider()
    s = d.dropna(subset=["net_yield"]).copy()
    if len(s) >= 40:
        fig = px.scatter(s, x=col, y="net_yield", color="district" if "district" in s.columns else None,
                         opacity=0.55, title="Scatter: charges vs net yield")
        fig.update_layout(xaxis_title="AED / sqm / year", yaxis_title="Net yield (%)")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
