import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme


hero("Pricing", "Pricing structure, dispersion & drivers (descriptive only).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

if "price_per_sqm" not in view.columns:
    st.error("Missing price_per_sqm column (facts mapping not applied).")
    st.stop()

d = view.dropna(subset=["price_per_sqm"]).copy()

# Cards
c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Listings", f"{len(view):,}", "Selection size")
with c2: kpi_card("Price/sqm coverage", f"{view['price_per_sqm'].notna().mean():.0%}", "Non-null share")
with c3: kpi_card("Median AED/sqm", f"{int(d['price_per_sqm'].median()):,}" if len(d) else "n/a", "Central pricing")
with c4: kpi_card("P90 AED/sqm", f"{int(d['price_per_sqm'].quantile(0.9)):,}" if len(d) else "n/a", "Upper pricing")

st.divider()

# Dist + box
fig = px.box(d, x="district" if "district" in d.columns else None, y="price_per_sqm", points=False, title="AED/sqm dispersion (box) by district")
fig.update_layout(xaxis_title="District", yaxis_title="AED per sqm")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

# Bedrooms curve
if "bedrooms" in d.columns:
    g = d.dropna(subset=["bedrooms"]).groupby(["district","bedrooms"])["price_per_sqm"].median().reset_index()
    fig = px.line(g, x="bedrooms", y="price_per_sqm", color="district", markers=True, title="Median AED/sqm vs Bedrooms (by district)")
    fig.update_layout(xaxis_title="Bedrooms", yaxis_title="Median AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

# Size vs price
if "size_sqm" in d.columns:
    s = d.dropna(subset=["size_sqm"]).copy()
    if len(s) >= 30:
        fig = px.scatter(s, x="size_sqm", y="price_per_sqm", color="district" if "district" in s.columns else None,
                         opacity=0.55, title="Scatter: size (sqm) vs AED/sqm")
        fig.update_layout(xaxis_title="Size (sqm)", yaxis_title="AED per sqm")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
