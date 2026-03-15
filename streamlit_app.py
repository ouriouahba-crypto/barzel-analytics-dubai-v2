import streamlit as st
import importlib.util
from pathlib import Path

st.set_page_config(page_title="Barzel Analytics — Dubai (V2)", layout="wide")

from src.app.ui import hero, load_data, inject_lovable_skin, top_nav
from src.app.translations import get_text
from src.processing.assemble import assemble


def run_page(filename: str):
    path = Path("pages") / filename
    spec = importlib.util.spec_from_file_location(filename, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)


# Initialize language state
if "language" not in st.session_state:
    st.session_state["language"] = "en"

if "df" not in st.session_state:
    st.session_state["df"] = assemble(load_data())

df = st.session_state["df"]

inject_lovable_skin()

# Premium language selector in header
col_title, col_lang = st.columns([5, 0.8], gap="large")

with col_title:
    lang = st.session_state.get("language", "en")
    hero(
        get_text("app_title", lang),
        get_text("app_subtitle", lang),
    )

with col_lang:
    st.markdown("<div style='padding-top:24px;'></div>", unsafe_allow_html=True)
    lang_choice = st.selectbox(
        get_text("language_label", lang),
        options=["EN", "FR"],
        index=0 if st.session_state.get("language") == "en" else 1,
        label_visibility="collapsed",
        key="lang_selector",
    )
    if lang_choice == "EN":
        st.session_state["language"] = "en"
    elif lang_choice == "FR":
        st.session_state["language"] = "fr"
    
    # Force rerun to apply language change
    if st.session_state.get("language") != lang:
        st.rerun()

lang = st.session_state.get("language", "en")


# Navigation with premium labels (simplified to 4 main pages)
NAV = [
    (get_text("nav_snapshot", lang), "1_Executive_Snapshot.py"),
    (get_text("nav_compare", lang), "2_Compare.py"),
    (get_text("nav_map", lang), "3_Map_Micro.py"),
    (get_text("nav_report", lang), "4_PDF_Memo_Builder.py"),
]

labels = [x[0] for x in NAV]
active = st.session_state.get("nav_active", labels[0])
active = top_nav(active=active, items=labels)
st.session_state["nav_active"] = active

# Coverage line (premium alternative to debug captions)
districts_list = sorted([d for d in df["district"].dropna().unique()]) if "district" in df.columns else []
coverage_prefix = get_text("coverage_prefix", lang)
listings_count = get_text("listings_count", lang)
districts_count = get_text("districts_count", lang)
coverage_text = f"{coverage_prefix} {len(df):,} {listings_count} • {len(districts_list)} {districts_count}"
st.markdown(f'<div class="ba-coverage">{coverage_text}</div>', unsafe_allow_html=True)

st.divider()

for label, file in NAV:
    if label == active:
        run_page(file)
        break
