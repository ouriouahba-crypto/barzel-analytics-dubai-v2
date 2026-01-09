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


# Load once (fast) + keep in session
if "df" not in st.session_state:
    st.session_state["df"] = assemble(load_data())

df = st.session_state["df"]

inject_lovable_skin()

hero(
    "Barzel Analytics — Dubai (V2)",
    "Analytical cockpit (no decision in UI). The PDF memo contains the decision narrative.",
)

# Top navigation (Lovable-like)
NAV = [
    ("Overview", "1_Executive_Snapshot.py"),
    ("Compare", "2_Compare.py"),
    ("Map", "3_Map_Micro.py"),
    ("PDF", "4_PDF_Memo_Builder.py"),
]

labels = [x[0] for x in NAV]
active = st.session_state.get("nav_active", labels[0])
active = top_nav(active=active, items=labels)
st.session_state["nav_active"] = active

# Small “status row” like a real SaaS
c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    st.caption(f"Rows: **{len(df):,}**")
with c2:
    st.caption(f"Columns: **{len(df.columns):,}**")
with c3:
    if "district" in df.columns:
        st.caption("Districts: " + ", ".join(sorted([d for d in df["district"].dropna().unique()])))

st.divider()

# Route to the right page file
for label, file in NAV:
    if label == active:
        run_page(file)
        break
