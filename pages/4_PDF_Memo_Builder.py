import streamlit as st

from src.app.ui import hero, selection_bar, section_intro
from src.app.translations import get_text
from src.app.pdf_report import ReportConfig, build_pdf_report

lang = st.session_state.get("language", "en")

hero(get_text("report_builder_title", lang), get_text("report_builder_subtitle", lang))

df_all = st.session_state.get("df")
if df_all is None or df_all.empty:
    st.stop()

districts = sorted(df_all["district"].dropna().unique().tolist()) if "district" in df_all.columns else []

# Configuration section
section_intro(get_text("section_report_config", lang), get_text("config_subtitle", lang))

col1, col2 = st.columns([1.5, 1.5])
with col1:
    profiles = [get_text("profile_capital_preservation", lang), get_text("profile_core", lang), get_text("profile_core_plus", lang), get_text("profile_opportunistic", lang)]
    investor_profile = st.selectbox(get_text("label_investor_profile", lang), profiles, index=0)

with col2:
    st.markdown(f"<p style='font-size:13px;color:#2D5A91;margin-top:1.8rem;'><strong>{get_text('label_dataset', lang)}</strong></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:13px;color:#1F4E79;'>{len(df_all):,} listings • {len(districts)} districts</p>", unsafe_allow_html=True)

st.markdown("")

# District selection
sel = selection_bar(
    districts,
    label=get_text("label_districts", lang),
    default=districts[:3] if len(districts) >= 3 else districts,
)

st.markdown("")

# Context notes
st.markdown(f"<p style='font-size:13px;color:#1F4E79;font-weight:600;margin-bottom:0.5rem;'>{get_text('label_note_analyst_context', lang)}</p>", unsafe_allow_html=True)
notes = st.text_area(
    "Notes",
    height=140,
    placeholder=get_text("placeholder_analyst_notes", lang),
    label_visibility="collapsed",
)

st.markdown("")

df_view = df_all[df_all["district"].isin(sel)] if sel else df_all
cfg = ReportConfig(investor_profile=investor_profile, districts=sel, notes=notes, language=lang)

if st.button(get_text("btn_generate_pdf", lang), use_container_width=True):
    pdf_bytes = build_pdf_report(df_all=df_all, df_view=df_view, cfg=cfg)
    st.success(get_text("msg_pdf_generated", lang))
    st.download_button(
        get_text("btn_download_pdf", lang),
        data=pdf_bytes,
        file_name="barzel_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
