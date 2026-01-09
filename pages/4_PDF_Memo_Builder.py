import streamlit as st
from src.app.ui import hero

from src.app.pdf_memo import MemoConfig, build_pdf_memo


hero("PDF Memo Builder", "Decision narrative lives in the PDF (scores only in PDF).")

df = st.session_state.get("df")
if df is None or df.empty:
    st.stop()

cfg = MemoConfig()
pdf_bytes = build_pdf_memo(df, cfg)

st.download_button(
    "Download PDF memo",
    data=pdf_bytes,
    file_name="barzel_memo.pdf",
    mime="application/pdf",
    use_container_width=True,
)
