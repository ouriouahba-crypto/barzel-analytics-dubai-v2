import streamlit as st
import plotly.express as px

from src.app.ui import hero
from src.analytics.aggregations import group_stats


hero("Yield & Vacancy", "Gross/Net yield, vacancy, and return vs pricing (no score).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel_d = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel_d)] if sel_d else df

st.divider()

# Net yield by district & bedrooms
st.subheader("Net yield (median) by bedrooms")
if "bedrooms" in view.columns:
    t = group_stats(view, ["district","bedrooms"], "net_yield", min_n=10)
    if t.empty:
        st.info("Not enough yield data.")
    else:
        fig = px.line(t.sort_values(["district","bedrooms"]), x="bedrooms", y="q50", color="district", markers=True, title="Median net yield by bedrooms")
        fig.update_layout(xaxis_title="Bedrooms", yaxis_title="Net yield (median, %)")
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# Net vs Gross yield scatter
st.subheader("Gross vs Net yield (scatter)")
d = view.dropna(subset=["gross_yield","net_yield"])
if len(d) < 30:
    st.info("Not enough data.")
else:
    fig = px.scatter(
        d,
        x="gross_yield",
        y="net_yield",
        color="district" if "district" in d.columns else None,
        opacity=0.45,
        hover_data=[c for c in ["bedrooms","building_name","vacancy_days"] if c in d.columns],
        title="Gross yield vs Net yield"
    )
    fig.update_layout(xaxis_title="Gross yield (%)", yaxis_title="Net yield (%)")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Yield vs Pricing
st.subheader("Yield vs Pricing (net yield vs AED/sqm)")
d = view.dropna(subset=["net_yield","price_per_sqm"])
if len(d) < 30:
    st.info("Not enough data.")
else:
    fig = px.scatter(
        d,
        x="price_per_sqm",
        y="net_yield",
        color="district" if "district" in d.columns else None,
        opacity=0.45,
        hover_data=[c for c in ["bedrooms","building_name","size_sqm"] if c in d.columns],
        title="Net yield vs AED/sqm"
    )
    fig.update_layout(xaxis_title="AED/sqm", yaxis_title="Net yield (%)")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Vacancy distribution
st.subheader("Vacancy days distribution")
if "vacancy_days" in view.columns:
    v = view.dropna(subset=["vacancy_days"])
    if len(v) < 20:
        st.info("Not enough vacancy data.")
    else:
        fig = px.histogram(v, x="vacancy_days", nbins=40, title="Vacancy days distribution")
        fig.update_layout(xaxis_title="Vacancy days", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No vacancy_days column.")
