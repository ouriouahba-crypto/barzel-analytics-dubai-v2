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
            max-width: 1440px;
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

        /* Radio buttons (nav) */
        .stRadio > label {
            flex-direction: row !important;
            gap: 0 !important;
        }
        .stRadio > label > span:first-child {
            display: none !important;
        }
        div[role="radiogroup"] {
            flex-wrap: nowrap !important;
            gap: 4px !important;
        }
        div[role="radiogroup"] > label {
            border-radius: 999px !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            background: rgba(255,255,255,0.04) !important;
            padding: 0.5rem 1rem !important;
            margin: 0 !important;
            font-size: 13px !important;
            transition: all 120ms ease !important;
            cursor: pointer !important;
            white-space: nowrap !important;
        }
        div[role="radiogroup"] > label:hover {
            border-color: rgba(0,229,168,0.30) !important;
            background: rgba(0,229,168,0.08) !important;
        }
        div[role="radiogroup"] > label > span:first-child {
            display: none !important;
        }
        div[role="radiogroup"] > label > span:last-child {
            color: rgba(229,231,235,0.92) !important;
        }
        .stRadio [role="radio"][aria-checked="true"] + span,
        .stRadio > label:has(input:checked) {
            border-color: rgba(0,229,168,0.50) !important;
            background: rgba(0,229,168,0.15) !important;
            color: rgba(0,229,168,0.95) !important;
        }
        .stRadio > label:has(input:checked) > span:last-child {
            color: rgba(0,229,168,0.95) !important;
            font-weight: 600 !important;
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

        /* Selection bar (premium container) */
        .ba-selection-bar {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 1.4rem;
        }

        /* Coverage line (premium caption) */
        .ba-coverage {
            color: rgba(229,231,235,0.65);
            font-size: 13px;
            letter-spacing: 0.01em;
            margin: 0.8rem 0 1.2rem 0;
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
    """Premium horizontal navigation using st.radio (no wrapping)."""
    col1, col_nav, col2 = st.columns([1.2, 3.0, 1.8], gap="medium")
    
    with col1:
        st.markdown(
            "<div style='font-weight:900;letter-spacing:-0.03em;font-size:18px;padding-top:10px;'>Barzel Analytics</div>"
            "<div style='color:rgba(229,231,235,0.55);font-size:12px;margin-top:-2px;'>Dubai</div>",
            unsafe_allow_html=True,
        )
    
    with col_nav:
        selected = st.radio(
            "Navigation",
            items,
            index=items.index(active) if active in items else 0,
            horizontal=True,
            label_visibility="collapsed",
        )
    
    with col2:
        st.markdown(
            "<div style='text-align:right;color:rgba(229,231,235,0.55);font-size:12px;padding-top:10px;'>"
            "<strong>Institutional Suite</strong></div>",
            unsafe_allow_html=True,
        )
    
    st.divider()
    return selected


def selection_bar(options: list, label: str = "Districts", default: list = None, key: str = None) -> list:
    """Premium selection bar (thin card with selector)."""
    st.markdown('<div class="ba-selection-bar">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.4, 3], gap="small")
    with col1:
        st.markdown("<span style='font-size:13px;color:rgba(229,231,235,0.75);font-weight:600;'>" + label + "</span>", unsafe_allow_html=True)
    
    with col2:
        if default is None:
            default = options[:3] if len(options) >= 3 else options
        selected = st.multiselect(
            label,
            options,
            default=default,
            key=key,
            label_visibility="collapsed",
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    return selected if selected else options


def format_metric(value: float, metric_type: str = "number") -> str:
    """Smart formatting for metrics without changing underlying values."""
    if value != value:  # NaN check
        return "n/a"
    
    if metric_type == "percentage":
        return f"{value:.2%}"
    elif metric_type == "basis_points":
        if value < 0.01:
            return f"{value*10000:.1f} bps"
        else:
            return f"{value:.2%}"
    elif metric_type == "small_ratio":
        # For ratios like yield efficiency that are < 0.01
        if value < 0.01 and value > 0:
            return f"{value*100:.3f}%"
        return f"{value:.2f}"
    elif metric_type == "price":
        return f"{int(value):,}"
    elif metric_type == "count":
        return f"{int(value):,}"
    else:
        return f"{value:.2f}"


def render_plotly_chart(fig, use_container_width: bool = True):
    """Render Plotly chart with consistent config (modebar hidden)."""
    st.plotly_chart(
        fig,
        use_container_width=use_container_width,
        config={"displayModeBar": False, "responsive": True},
    )


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
