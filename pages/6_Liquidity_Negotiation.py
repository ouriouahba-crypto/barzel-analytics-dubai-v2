import streamlit as st
import plotly.express as px

from src.app.ui import hero, kpi_card, apply_plotly_theme


hero("Liquidity", "Time-to-exit, depth & pricing discipline (descriptive only).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

districts = sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else []
sel = st.multiselect("Districts", districts, default=districts[:3] if len(districts) >= 3 else districts)
view = df[df["district"].isin(sel)] if sel else df

need = ["days_on_market", "price_per_sqm"]
missing = [c for c in need if c not in view.columns]
if missing:
    st.error(f"Missing columns for liquidity analysis: {missing}")
    st.stop()

d = view.dropna(subset=["days_on_market"]).copy()

# Cards
c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Listings", f"{len(view):,}", "Selection size")
with c2: kpi_card("DOM coverage", f"{view['days_on_market'].notna().mean():.0%}", "Non-null share")
with c3: kpi_card("Median DOM", f"{int(d['days_on_market'].median()):,}" if len(d) else "n/a", "Exit speed")
with c4: kpi_card("Fast-sale ≤30d", f"{(d['days_on_market'] <= 30).mean():.0%}" if len(d) else "n/a", "Liquidity signal")

st.divider()

# DOM distribution
fig = px.histogram(d, x="days_on_market", nbins=45, title="Distribution: Days on Market")
fig.update_layout(xaxis_title="Days on Market", yaxis_title="Count")
st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

# Price vs DOM scatter
s = view.dropna(subset=["price_per_sqm", "days_on_market"]).copy()
if len(s) >= 40:
    fig = px.scatter(
        s,
        x="price_per_sqm",
        y="days_on_market",
        color="district" if "district" in s.columns else None,
        opacity=0.55,
        title="Scatter: AED/sqm vs Days on Market (pricing discipline)",
        hover_data=[c for c in ["building_name", "bedrooms", "size_sqm"] if c in s.columns],
    )
    fig.update_layout(xaxis_title="AED per sqm", yaxis_title="Days on Market")
    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

st.divider()

# Fast-sale table by district
if "district" in view.columns:
    t = view.dropna(subset=["days_on_market"]).groupby("district")["days_on_market"].agg(
        n="count",
        median="median",
        fast_30=lambda x: (x <= 30).mean(),
        fast_60=lambda x: (x <= 60).mean(),
    ).reset_index()
    st.subheader("District liquidity table")
    st.dataframe(t.sort_values("n", ascending=False), use_container_width=True)
