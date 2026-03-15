import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme, section_intro, chart_explanation
from src.app.translations import get_text

lang = st.session_state.get("language", "en")

hero(get_text("pricing_title", lang), get_text("pricing_subtitle", lang))

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = st.multiselect(get_text("label_districts", lang), districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

if "price_per_sqm" not in view.columns:
    st.error("Missing price_per_sqm column (facts mapping not applied).")
    st.stop()

d = view.dropna(subset=["price_per_sqm"]).copy()

# Cards
c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card(get_text("kpi_listings", lang), f"{len(view):,}", get_text("selection_size", lang))
with c2: kpi_card(get_text("kpi_price_sqm_coverage", lang), f"{view['price_per_sqm'].notna().mean():.0%}", get_text("non_null_share", lang))
with c3: kpi_card(get_text("kpi_median_aed_sqm", lang), f"{int(d['price_per_sqm'].median()):,}" if len(d) else "n/a", get_text("central_pricing", lang))
with c4: kpi_card(get_text("kpi_p90_aed_sqm", lang), f"{int(d['price_per_sqm'].quantile(0.9)):,}" if len(d) else "n/a", get_text("upper_pricing", lang))

st.divider()

# Dist + box
section_intro(get_text("section_price_dispersion", lang), get_text("price_disp_subtitle", lang))
chart_explanation(get_text("price_disp_explanation", lang))
fig = px.box(d, x="district" if "district" in d.columns else None, y="price_per_sqm", points=False, title=get_text("chart_aed_dispersion", lang))
fig.update_layout(xaxis_title="District", yaxis_title="AED per sqm")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

# Bedrooms curve
if "bedrooms" in d.columns:
    section_intro(get_text("section_product_pricing", lang), get_text("product_pricing_sub", lang))
    chart_explanation(get_text("product_explanation", lang))
    g = d.dropna(subset=["bedrooms"]).groupby(["district","bedrooms"])["price_per_sqm"].median().reset_index()
    fig = px.line(g, x="bedrooms", y="price_per_sqm", color="district", markers=True, title=get_text("chart_median_by_bedroom", lang))
    fig.update_layout(xaxis_title="Bedrooms", yaxis_title="Median AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

# Size vs price
if "size_sqm" in d.columns:
    section_intro(get_text("section_size_pricing", lang), get_text("size_pricing_sub", lang))
    chart_explanation(get_text("size_explanation", lang))
    s = d.dropna(subset=["size_sqm"]).copy()
    if len(s) >= 30:
        fig = px.scatter(s, x="size_sqm", y="price_per_sqm", color="district" if "district" in s.columns else None,
                         opacity=0.55, title=get_text("chart_unit_size_efficiency", lang))
        fig.update_layout(xaxis_title="Size (sqm)", yaxis_title="AED per sqm")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
