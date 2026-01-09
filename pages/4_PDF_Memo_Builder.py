import streamlit as st

from src.app.ui import hero
from src.app.pdf_memo import MemoConfig, build_pdf_memo


hero("PDF Memo Builder", "Scores + decision narrative live here (PDF-only).")

df_all = st.session_state.get("df")
if df_all is None or df_all.empty:
    st.stop()

districts = sorted(df_all["district"].dropna().unique().tolist()) if "district" in df_all.columns else []

investor_profile = st.selectbox(
    "Investor profile",
    ["Capital Preservation", "Core", "Core+", "Opportunistic"],
    index=0,
)

sel = st.multiselect("Districts included in memo", districts, default=districts[:3] if len(districts) >= 3 else districts)

notes = st.text_area("Analyst notes (optional)", height=120, placeholder="Key assumptions, risk notes, constraints...")

df_view = df_all[df_all["district"].isin(sel)] if sel else df_all

cfg = MemoConfig(investor_profile=investor_profile, districts=sel, notes=notes)

if st.button("Generate PDF memo"):
    pdf_bytes = build_pdf_memo(df_all=df_all, df_view=df_view, cfg=cfg)
    st.success("PDF generated.")
    st.download_button(
        "Download memo.pdf",
        data=pdf_bytes,
        file_name="barzel_memo_v2.pdf",
        mime="application/pdf",
    )
