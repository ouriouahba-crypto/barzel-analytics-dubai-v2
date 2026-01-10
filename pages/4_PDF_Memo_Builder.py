import streamlit as st

from src.app.ui import hero
from src.app.pdf_report import ReportConfig, build_pdf_report


hero("PDF Report Builder", "Full analyst-style report: Understand → Score (detailed) → Decide")

df_all = st.session_state.get("df")
if df_all is None or df_all.empty:
    st.stop()

districts = sorted(df_all["district"].dropna().unique().tolist()) if "district" in df_all.columns else []

profiles = ["Capital Preservation", "Core", "Core+", "Opportunistic"]
investor_profile = st.selectbox("Investor profile", profiles, index=0)

sel = st.multiselect(
    "Districts",
    districts,
    default=districts[:3] if len(districts) >= 3 else districts,
)

notes = st.text_area(
    "Client context / analyst notes (optional)",
    height=180,
    placeholder="Context, constraints, objectives, any special instructions...",
)

df_view = df_all[df_all["district"].isin(sel)] if sel else df_all
cfg = ReportConfig(investor_profile=investor_profile, districts=sel, notes=notes)

if st.button("Generate PDF report", use_container_width=True):
    pdf_bytes = build_pdf_report(df_all=df_all, df_view=df_view, cfg=cfg)

    st.success("PDF generated.")
    st.download_button(
        "Download barzel_report_v2.pdf",
        data=pdf_bytes,
        file_name="barzel_report_v2.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
