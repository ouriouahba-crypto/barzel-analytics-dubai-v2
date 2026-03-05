import streamlit as st
import importlib.util
from pathlib import Path

st.set_page_config(page_title="Barzel Analytics — Dubai (V2)", layout="wide")

from src.app.ui import hero, load_data, inject_lovable_skin, top_nav
from src.processing.assemble import assemble


def run_page(filename: str):
    path = Path("pages") / filename
    spec = importlib.util.spec_from_file_location(filename, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)


if "df" not in st.session_state:
    st.session_state["df"] = assemble(load_data())

df = st.session_state["df"]

inject_lovable_skin()

hero(
    "Barzel Analytics — Dubai (V2)",
    "Institutional analytical cockpit. Premium analytics for funds and family offices.",
)

# Navigation with premium labels (simplified to 4 main pages)
NAV = [
    ("Executive Snapshot", "1_Executive_Snapshot.py"),
    ("Compare", "2_Compare.py"),
    ("Map & Micro", "3_Map_Micro.py"),
    ("PDF Report", "4_PDF_Memo_Builder.py"),
]

labels = [x[0] for x in NAV]
active = st.session_state.get("nav_active", labels[0])
active = top_nav(active=active, items=labels)
st.session_state["nav_active"] = active

# Coverage line (premium alternative to debug captions)
districts_list = sorted([d for d in df["district"].dropna().unique()]) if "district" in df.columns else []
coverage_text = f"Coverage: {len(df):,} listings • {len(districts_list)} districts"
st.markdown(f'<div class="ba-coverage">{coverage_text}</div>', unsafe_allow_html=True)

st.divider()

for label, file in NAV:
    if label == active:
        run_page(file)
        break
