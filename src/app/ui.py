import pandas as pd
import streamlit as st
from pathlib import Path


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    path = Path("data/listings_enriched.csv")
    if not path.exists():
        st.error(f"Missing dataset: {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)

    # Minimal normalization (safe)
    if "district" in df.columns:
        df["district"] = df["district"].astype(str)

    for c in ["price", "size_sqm", "latitude", "longitude"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    for c in ["first_seen", "last_seen"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", utc=True)

    return df


def inject_lovable_skin():
    st.markdown(
        """
        <style>
        /* Kill Streamlit chrome */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stToolbar"] {visibility: hidden;}
        [data-testid="stStatusWidget"] {visibility: hidden;}
        [data-testid="stDecoration"] {display: none;}

        /* Layout */
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2.0rem;
            max-width: 1240px;
        }

        html, body, [class*="css"] {
            font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
        }

        /* Cards */
        .ba-card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 18px;
            padding: 16px 16px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.28);
        }
        .ba-card:hover {
            border-color: rgba(0,229,168,0.22);
            box-shadow: 0 14px 48px rgba(0,0,0,0.32);
        }

        .ba-title {
            font-size: 12px;
            letter-spacing: 0.10em;
            text-transform: uppercase;
            color: rgba(229,231,235,0.70);
            margin-bottom: 8px;
        }
        .ba-value {
            font-size: 26px;
            font-weight: 780;
            letter-spacing: -0.02em;
            color: rgba(229,231,235,0.95);
            line-height: 1.1;
        }
        .ba-sub {
            margin-top: 6px;
            font-size: 12px;
            color: rgba(229,231,235,0.62);
        }

        /* Buttons (pills) */
        .stButton>button {
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(255,255,255,0.06);
            color: rgba(229,231,235,0.92);
            padding: 0.55rem 0.9rem;
            transition: all 120ms ease;
        }
        .stButton>button:hover {
            border-color: rgba(0,229,168,0.30);
            background: rgba(0,229,168,0.10);
            transform: translateY(-1px);
        }

        /* Tables */
        .stDataFrame, [data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.09);
        }

        /* Dividers */
        hr {
            border: none;
            border-top: 1px solid rgba(255,255,255,0.06);
            margin: 1.2rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str):
    st.markdown(
        f"""
        <div style="
            padding: 0.9rem 0 1.1rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.07);
            margin-bottom: 1.2rem;
        ">
          <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:16px;">
            <div>
              <h1 style="margin:0;letter-spacing:-0.03em;font-size:2.1rem;">{title}</h1>
              <p style="color:rgba(229,231,235,0.62);margin:0.35rem 0 0 0;font-size:1.05rem;max-width:860px;">
                {subtitle}
              </p>
            </div>
            <div style="text-align:right;color:rgba(229,231,235,0.45);font-size:12px;padding-bottom:6px;">
              Dubai V2 • Analytical Cockpit
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(title: str, value: str, sub: str = ""):
    st.markdown(
        f"""
        <div class="ba-card">
          <div class="ba-title">{title}</div>
          <div class="ba-value">{value}</div>
          <div class="ba-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def top_nav(active: str, items: list[str]) -> str:
    cols = st.columns([1.3, *([1] * len(items)), 2.0])

    with cols[0]:
        st.markdown(
            "<div style='font-weight:900;letter-spacing:-0.03em;font-size:18px;'>Barzel Analytics</div>"
            "<div style='color:rgba(229,231,235,0.55);font-size:12px;margin-top:-2px;'>Dubai</div>",
            unsafe_allow_html=True,
        )

    selected = active
    for i, it in enumerate(items, start=1):
        with cols[i]:
            if st.button(it, use_container_width=True):
                selected = it

    with cols[-1]:
        st.markdown(
            "<div style='text-align:right;color:rgba(229,231,235,0.45);font-size:12px;padding-top:8px;'>"
            "No score in UI • Scores only in PDF</div>",
            unsafe_allow_html=True,
        )

    st.divider()
    return selected


def apply_plotly_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="rgba(229,231,235,0.92)",
        title_font_size=16,
        margin=dict(l=10, r=10, t=55, b=10),
        legend=dict(font=dict(color="rgba(229,231,235,0.80)")),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.08)")
    return fig
