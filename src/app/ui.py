import pandas as pd
import streamlit as st
from pathlib import Path
from src.app.translations import get_text


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

        /* Premium color palette */
        :root {
            --ba-bg-primary: #FAF8F4;
            --ba-bg-secondary: #F3F0EA;
            --ba-card-bg: #FFFFFF;
            --ba-border: #E7E2D9;
            --ba-text-primary: #1F4E79;
            --ba-text-secondary: #2D5A91;
            --ba-accent-light: #F0F4F8;
        }

        /* Page background - warm light institutional */
        .stApp, [data-testid="stAppViewContainer"] {
            background-color: #FAF8F4;
        }

        /* Layout */
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2.0rem;
            max-width: 1440px;
            background-color: #FAF8F4;
        }

        html, body, [class*="css"] {
            font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
        }

        /* Premium cards - white with elegant border */
        .ba-card {
            background: #FFFFFF;
            border: 1px solid #E7E2D9;
            border-radius: 12px;
            padding: 18px 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        .ba-card:hover {
            border-color: #D9CFC0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        /* Shared chart and data containers */
        [data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {
            background: #FFFFFF;
            border: 1px solid #E7E2D9;
            border-radius: 12px;
            padding: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }

        [data-testid="stAlert"] {
            background: #F9F8F5;
            border: 1px solid #E7E2D9;
            color: #1F4E79;
            border-radius: 10px;
        }

        .ba-title {
            font-size: 11px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: #1F4E79;
            margin-bottom: 8px;
        }
        .ba-value {
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: #1F4E79;
            line-height: 1.1;
        }
        .ba-sub {
            margin-top: 6px;
            font-size: 12px;
            color: #2D5A91;
        }

        /* Buttons (pills) */
        .stButton>button {
            border-radius: 8px;
            border: 1px solid #E7E2D9;
            background: #FFFFFF;
            color: #1F4E79;
            padding: 0.55rem 0.9rem;
            transition: all 120ms ease;
            font-weight: 500;
        }
        .stButton>button:hover {
            border-color: #1F4E79;
            background: #F0F4F8;
            color: #1F4E79;
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
            gap: 6px !important;
        }
        div[role="radiogroup"] > label {
            border-radius: 8px !important;
            border: 1px solid #E7E2D9 !important;
            background: #FFFFFF !important;
            padding: 0.5rem 1rem !important;
            margin: 0 !important;
            font-size: 13px !important;
            transition: all 120ms ease !important;
            cursor: pointer !important;
            white-space: nowrap !important;
            color: #1F4E79 !important;
        }
        div[role="radiogroup"] > label:hover {
            border-color: #1F4E79 !important;
            background: #F0F4F8 !important;
        }
        div[role="radiogroup"] > label > span:first-child {
            display: none !important;
        }
        div[role="radiogroup"] > label > span:last-child {
            color: #1F4E79 !important;
        }
        div[role="radiogroup"] > label:has(input:checked) {
            border-color: #1F4E79 !important;
            background: #F0F4F8 !important;
            color: #1F4E79 !important;
        }
        div[role="radiogroup"] > label:has(input:checked) > span:last-child {
            color: #1F4E79 !important;
            font-weight: 600 !important;
        }

        /* Tables */
        .stDataFrame, [data-testid="stDataFrame"] {
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #E7E2D9;
        }

        /* Table text - all blue */
        [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
            color: #1F4E79 !important;
        }

        /* Dividers */
        hr {
            border: none;
            border-top: 1px solid #E7E2D9;
            margin: 1.2rem 0;
        }

        /* Selection bar (light card container) */
        .ba-selection-bar {
            background: #FFFFFF;
            border: 1px solid #E7E2D9;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 1.4rem;
        }

        /* Coverage line */
        .ba-coverage {
            color: #2D5A91;
            font-size: 13px;
            letter-spacing: 0.01em;
            margin: 0.8rem 0 1.2rem 0;
        }

        /* Institutional text styles for new helpers */
        .ba-section-intro {
            margin-bottom: 1.2rem;
        }
        .ba-section-title {
            font-size: 18px;
            font-weight: 600;
            color: #1F4E79;
            margin: 0 0 0.3rem 0;
        }
        .ba-section-subtitle {
            font-size: 14px;
            color: #2D5A91;
            margin: 0;
        }

        /* Explanation block - premium pale background */
        .ba-explanation {
            background: #F9F8F5;
            border-left: 2px solid #1F4E79;
            border-radius: 4px;
            padding: 12px 14px;
            margin: 14px 0;
            font-size: 13px;
            color: #1F4E79;
            line-height: 1.6;
            font-style: normal;
        }

        /* Insight box - premium subtle styling */
        .ba-insight-box {
            background: #FAF8F4;
            border: 1px solid #E7E2D9;
            border-left: 3px solid #1F4E79;
            border-radius: 6px;
            padding: 14px 16px;
            margin-bottom: 0.8rem;
        }
        .ba-insight-title {
            font-size: 13px;
            font-weight: 600;
            color: #1F4E79;
            margin: 0 0 0.4rem 0;
        }
        .ba-insight-text {
            font-size: 13px;
            color: #1F4E79;
            margin: 0;
            line-height: 1.5;
        }

        /* Takeaway - institutional note */
        .ba-takeaway {
            background: #FAF8F4;
            border-left: 3px solid #1F4E79;
            border-radius: 4px;
            padding: 11px 14px;
            margin-top: 0.8rem;
            font-size: 13px;
            color: #1F4E79;
            font-style: normal;
        }

        .ba-metric-group-label {
            font-size: 13px;
            font-weight: 600;
            color: #1F4E79;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin: 1.4rem 0 0.8rem 0;
            padding-top: 0.8rem;
            border-top: 1px solid #E7E2D9;
        }

        /* Executive summary - premium styling */
        .ba-exec-summary {
            background: #F9F8F5;
            border-radius: 8px;
            padding: 16px 18px;
            margin-bottom: 1.6rem;
            border-left: 3px solid #1F4E79;
        }
        .ba-exec-summary-title {
            font-size: 14px;
            font-weight: 700;
            color: #1F4E79;
            margin: 0 0 0.8rem 0;
        }
        .ba-exec-summary-points {
            margin: 0;
        }
        .ba-exec-summary-points li {
            font-size: 14px;
            color: #1F4E79;
            margin-bottom: 0.6rem;
            line-height: 1.5;
        }
        /* Selectbox for language selector */
        .stSelectbox > div > div {
            border-radius: 6px;
        }

        .stMultiSelect [data-baseweb="select"] > div,
        .stSelectbox [data-baseweb="select"] > div,
        .stTextArea textarea {
            background: #FFFFFF !important;
            border: 1px solid #E7E2D9 !important;
            color: #1F4E79 !important;
            border-radius: 10px !important;
        }
        
        .ba-coverage {
            font-size: 12px;
            color: #2D5A91;
            margin: 0 0 1rem 0;
            font-weight: 500;
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
            border-bottom: 1px solid #E7E2D9;
            margin-bottom: 1.2rem;
        ">
          <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:16px;">
            <div>
              <h1 style="margin:0;letter-spacing:-0.03em;font-size:2.1rem;color:#1F4E79;">{title}</h1>
              <p style="color:#2D5A91;margin:0.35rem 0 0 0;font-size:1.05rem;max-width:860px;">
                {subtitle}
              </p>
            </div>
            <div style="text-align:right;color:#2D5A91;font-size:12px;padding-bottom:6px;">
              Dubai • Real Estate Analytics
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
            "<div style='font-weight:900;letter-spacing:-0.03em;font-size:18px;padding-top:10px;color:#1F4E79;'>Barzel Analytics</div>"
            "<div style='color:#2D5A91;font-size:12px;margin-top:-2px;'>Dubai</div>",
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
            "<div style='text-align:right;color:#2D5A91;font-size:12px;padding-top:10px;'>"
            "<strong>Real Estate Analytics</strong></div>",
            unsafe_allow_html=True,
        )
    
    st.divider()
    return selected


def selection_bar(options: list, label: str = "Districts", default: list = None, key: str = None) -> list:
    """Premium selection bar (thin card with selector)."""
    st.markdown('<div class="ba-selection-bar">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.4, 3], gap="small")
    with col1:
        st.markdown("<span style='font-size:13px;color:#1F4E79;font-weight:600;'>" + label + "</span>", unsafe_allow_html=True)
    
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


def narrative_text(en_text: str, fr_text: str) -> str:
    """Return French only for narrative copy when the app is in FR mode."""
    return fr_text if st.session_state.get("language", "en") == "fr" else en_text


def render_plotly_chart(fig, use_container_width: bool = True):
    """Render Plotly chart with consistent config (modebar hidden)."""
    st.plotly_chart(
        fig,
        use_container_width=use_container_width,
        config={"displayModeBar": False, "responsive": True},
    )


def apply_plotly_theme(fig):
    """Apply premium light institutional theme to Plotly figures - all text blue."""
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FAF8F4",
        font_color="#1F4E79",
        title_font_size=14,
        title_font_color="#1F4E79",
        title_font_family="Arial, sans-serif",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            font=dict(color="#1F4E79", size=12),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#E7E2D9",
            borderwidth=1
        ),
        hovermode="closest",
    )
    fig.update_xaxes(
        gridcolor="#F3F0EA", 
        zerolinecolor="#E7E2D9",
        title_font_color="#1F4E79",
        title_font_size=12,
        tickfont=dict(color="#2D5A91", size=11),
        showgrid=True,
        gridwidth=0.5
    )
    fig.update_yaxes(
        gridcolor="#F3F0EA", 
        zerolinecolor="#E7E2D9",
        title_font_color="#1F4E79",
        title_font_size=12,
        tickfont=dict(color="#2D5A91", size=11),
        showgrid=True,
        gridwidth=0.5
    )
    return fig

# ===== NEW INSTITUTIONAL UI HELPERS =====

def executive_summary(points: list[str]):
    """Render executive summary block with key insights."""
    if not points:
        return
    html = '<div class="ba-exec-summary"><div class="ba-exec-summary-title">Key Insights</div><ul class="ba-exec-summary-points">'
    for point in points:
        html += f"<li>{point}</li>"
    html += "</ul></div>"
    st.markdown(html, unsafe_allow_html=True)


def section_intro(title: str, subtitle: str = None):
    """Render section intro with title and optional subtitle."""
    html = '<div class="ba-section-intro">'
    html += f'<h3 class="ba-section-title">{title}</h3>'
    if subtitle:
        html += f'<p class="ba-section-subtitle">{subtitle}</p>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def insight_box(title: str, text: str, icon: str = "•"):
    """Render a highlighted insight box."""
    html = f'''<div class="ba-insight-box">
        <div class="ba-insight-title">{icon} {title}</div>
        <div class="ba-insight-text">{text}</div>
    </div>'''
    st.markdown(html, unsafe_allow_html=True)


def takeaway(text: str):
    """Render a one-line chart takeaway."""
    html = f'<div class="ba-takeaway">💡 {text}</div>'
    st.markdown(html, unsafe_allow_html=True)


def metric_group_label(text: str):
    """Render a label for grouped metrics."""
    html = f'<div class="ba-metric-group-label">{text}</div>'
    st.markdown(html, unsafe_allow_html=True)


def chart_explanation(text: str):
    """Render a clean explanation block for chart context."""
    html = f'<div class="ba-explanation">{text}</div>'
    st.markdown(html, unsafe_allow_html=True)


def premium_insight(insight: str, icon: str = "📊"):
    """Render a premium insight callout block."""
    html = f'''<div class="ba-insight-box">
        <div class="ba-insight-title">{icon} Key Insight</div>
        <div class="ba-insight-text">{insight}</div>
    </div>'''
    st.markdown(html, unsafe_allow_html=True)
