import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme


hero("Yield", "Income efficiency, yield dispersion & drivers (descriptive only).")

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

fig = px.histogram(d, x="net_yield", nbins=35, title="Distribution: Net yield (%)")
fig.update_layout(xaxis_title="Net yield (%)", yaxis_title="Count")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

if "price_per_sqm" in view.columns:
    s = view.dropna(subset=["price_per_sqm", "net_yield"]).copy()
    if len(s) >= 40:
        fig = px.scatter(
            s,
            x="price_per_sqm",
            y="net_yield",
            color="district" if "district" in s.columns else None,
            opacity=0.55,
            title="Scatter: AED/sqm vs Net yield",
        )
        fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Net yield (%)")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

# Vacancy (if present)
if "vacancy_days" in view.columns:
    st.divider()
    v = view.dropna(subset=["vacancy_days"]).copy()
    if len(v) >= 30:
        fig = px.histogram(v, x="vacancy_days", nbins=35, title="Vacancy days distribution (proxy)")
        fig.update_layout(xaxis_title="Vacancy days", yaxis_title="Count")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
