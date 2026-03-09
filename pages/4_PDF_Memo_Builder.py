import streamlit as st

from src.app.ui import hero, selection_bar
from src.app.pdf_report import ReportConfig, build_pdf_report


hero("PDF Report Builder", "Generate comprehensive analyst report with scores and recommendations.")

df_all = st.session_state.get("df")
if df_all is None or df_all.empty:
    st.stop()

districts = sorted(df_all["district"].dropna().unique().tolist()) if "district" in df_all.columns else []

# Configuration section
st.subheader("Report Configuration")

col1, col2 = st.columns([1.5, 1.5])
with col1:
    profiles = ["Capital Preservation", "Core", "Core+", "Opportunistic"]
    investor_profile = st.selectbox("Investor Profile", profiles, index=0)

with col2:
    st.markdown("<p style='font-size:13px;color:rgba(229,231,235,0.75);margin-top:1.8rem;'><strong>Dataset</strong></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:13px;color:rgba(229,231,235,0.55);'>{len(df_all):,} listings • {len(districts)} districts</p>", unsafe_allow_html=True)

st.markdown("")

# District selection
sel = selection_bar(
    districts,
    label="Districts",
    default=districts[:3] if len(districts) >= 3 else districts,
)

st.markdown("")

# Context notes
st.markdown("<p style='font-size:13px;color:rgba(229,231,235,0.75);font-weight:600;margin-bottom:0.5rem;'>Analyst Context (optional)</p>", unsafe_allow_html=True)
notes = st.text_area(
    "Notes",
    height=140,
    placeholder="Client context, constraints, objectives, special instructions...",
    label_visibility="collapsed",
)

st.markdown("")

df_view = df_all[df_all["district"].isin(sel)] if sel else df_all
cfg = ReportConfig(investor_profile=investor_profile, districts=sel, notes=notes)

if st.button("Generate PDF Report", use_container_width=True):
    pdf_bytes = build_pdf_report(df_all=df_all, df_view=df_view, cfg=cfg)
    st.success("✓ PDF generated successfully.")
    st.download_button(
        "Download barzel_report.pdf",
        data=pdf_bytes,
        file_name="barzel_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
