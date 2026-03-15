import streamlit as st
import plotly.express as px

from src.app.ui import (
    hero, kpi_card, selection_bar, apply_plotly_theme,
    section_intro, chart_explanation, premium_insight, narrative_text
)
from src.app.translations import get_text

lang = st.session_state.get("language", "en")

hero("Pricing Lab", "Pricing structure, dispersion & drivers (descriptive only).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = selection_bar(districts, label="Districts", default=districts[:3] if len(districts) >= 3 else districts)
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
section_intro("Price Dispersion by District", "Understanding pricing variability and outliers.")
chart_explanation(get_text("price_disp_explanation", lang))
fig = px.box(d, x="district" if "district" in d.columns else None, y="price_per_sqm", points=False, title="AED/sqm Dispersion by District")
fig.update_layout(xaxis_title="District", yaxis_title="AED per sqm")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
premium_insight(
    narrative_text(
        "Dispersion width helps separate tightly priced districts from markets with broader product or quality variation.",
        "L'ampleur de la dispersion permet de distinguer les districts a pricing serre de ceux ou le mix produit ou la qualite creent davantage d'ecarts.",
    ),
    "📦",
)

st.divider()

# Bedrooms curve
if "bedrooms" in d.columns:
    section_intro("Product Pricing Curve", "How price per sqm varies by unit size across districts.")
    chart_explanation(get_text("product_explanation", lang))
    g = d.dropna(subset=["bedrooms"]).groupby(["district","bedrooms"])["price_per_sqm"].median().reset_index()
    fig = px.line(g, x="bedrooms", y="price_per_sqm", color="district", markers=True, title="Median AED/sqm vs Bedroom Count")
    fig.update_layout(xaxis_title="Bedrooms", yaxis_title="Median AED per sqm")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
    premium_insight(
        narrative_text(
            "Steeper curves suggest stronger willingness to pay for larger formats within the same district.",
            "Des courbes plus pentues indiquent une disposition a payer plus marquee pour les formats plus grands au sein d'un meme district.",
        ),
        "📈",
    )

st.divider()

# Size vs price
if "size_sqm" in d.columns:
    section_intro("Size vs. Pricing Relationship", "Understanding unit scale pricing efficiency.")
    chart_explanation(get_text("size_explanation", lang))
    s = d.dropna(subset=["size_sqm"]).copy()
    if len(s) >= 30:
        fig = px.scatter(s, x="size_sqm", y="price_per_sqm", color="district" if "district" in s.columns else None,
                         opacity=0.55, title="Unit Size vs. Price Efficiency")
        fig.update_layout(xaxis_title="Size (sqm)", yaxis_title="AED per sqm")
        st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
        premium_insight(
            narrative_text(
                "This relationship helps show whether larger units trade at a discount per sqm or whether scarcity sustains premium pricing.",
                "Cette relation permet de voir si les grandes surfaces se negocient avec une decote au m2 ou si la rarete maintient une prime.",
            ),
            "📐",
        )
