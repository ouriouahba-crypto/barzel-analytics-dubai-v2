import streamlit as st
import plotly.express as px

from src.app.ui import hero
from src.analytics.aggregations import group_stats


hero("Costs & Charges", "Service charges, burdens, and impact on net yield (no score).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel_d = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel_d)] if sel_d else df

st.divider()

st.subheader("Service charge distribution (AED/sqm/year)")
d = view.dropna(subset=["service_charge_psm_year"])
if len(d) < 20:
    st.info("Not enough service charge data.")
else:
    fig = px.histogram(d, x="service_charge_psm_year", nbins=40, title="Service charge distribution")
    fig.update_layout(xaxis_title="AED/sqm/year", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Charges vs Net Yield (scatter)")
d = view.dropna(subset=["service_charge_psm_year","net_yield"])
if len(d) < 30:
    st.info("Not enough data.")
else:
    fig = px.scatter(
        d,
        x="service_charge_psm_year",
        y="net_yield",
        color="district" if "district" in d.columns else None,
        opacity=0.45,
        hover_data=[c for c in ["bedrooms","building_name","size_sqm"] if c in d.columns],
        title="Service charge vs Net yield"
    )
    fig.update_layout(xaxis_title="AED/sqm/year", yaxis_title="Net yield (%)")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Top buildings by highest charges (min sample)")
if "building_name" in view.columns:
    min_n = st.slider("Min listings per building", 5, 50, 15, step=5)
    tb = group_stats(view, ["district","building_name"], "service_charge_psm_year", min_n=min_n)
    if tb.empty:
        st.info("Not enough building data.")
    else:
        tb = tb.sort_values("q50", ascending=False)
        st.dataframe(tb.head(80), use_container_width=True)
else:
    st.info("No building_name column.")
