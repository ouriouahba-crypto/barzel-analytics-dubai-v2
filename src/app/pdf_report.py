from __future__ import annotations

import io
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.analytics.market_views import snapshot, snapshots_by
from src.analytics.scoring_pdf_only import barzel_score_details, barzel_scores_by_district


@dataclass
class ReportConfig:
    investor_profile: str
    districts: List[str]
    notes: str = ""
    report_title: str = "Dubai District Intelligence Report"
    subtitle: str = "Market situation, scoring methodology, and decision support"


def build_pdf_report(df_all: pd.DataFrame, df_view: pd.DataFrame, cfg: ReportConfig) -> bytes:
    """
    10–20 pages analyst-style PDF:
    Understand -> Score (detailed) -> Decide
    """
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title=cfg.report_title,
        author="Barzel Analytics",
    )

    styles = _styles()
    story = []

    # Cover
    story += _cover(cfg, styles)
    story.append(PageBreak())

    # TOC (manual)
    story += _toc(cfg, styles)
    story.append(PageBreak())

    # A) Understand
    story += _section_header("A. Market situation (Understand)", styles)
    story += _executive_overview(df_view, cfg, styles)
    story += _scope_and_data_quality(df_view, cfg, styles)
    story += _kpi_glossary(styles)
    story += _market_overview(df_view, styles)
    story.append(PageBreak())

    # B) District profiles
    story += _section_header("B. District profiles", styles)
    for d in cfg.districts:
        sub = df_view[df_view["district"].astype(str) == str(d)] if "district" in df_view.columns else df_view
        story += _district_profile(d, sub, styles)
        story.append(PageBreak())

    # C) Comparison (facts)
    story += _section_header("C. Cross-district comparison (facts)", styles)
    story += _comparison_facts(df_view, styles)
    story.append(PageBreak())

    # D) Scoring
    story += _section_header("D. Scoring (methodology + detailed calculations)", styles)
    story += _scoring_methodology(cfg, styles)

    example_district = cfg.districts[0] if cfg.districts else "All"
    ex_df = (
        df_view[df_view["district"].astype(str) == str(example_district)]
        if "district" in df_view.columns and example_district != "All"
        else df_view
    )
    story += _scoring_details(df_all, ex_df, example_district, styles)
    story += _scoring_results(df_all, df_view, cfg, styles)
    story.append(PageBreak())

    # E) Decide
    story += _section_header("E. Decision support", styles)
    story += _decision_support(df_all, df_view, cfg, styles)
    story += _action_plan(df_all, df_view, cfg, styles)

    # Appendix
    story.append(PageBreak())
    story += _section_header("Appendix", styles)
    story += _appendix_tables(df_view, styles)

    doc.build(
        story,
        onFirstPage=lambda c, d: _draw_header_footer(c, d, cfg, first_page=True),
        onLaterPages=lambda c, d: _draw_header_footer(c, d, cfg, first_page=False),
    )

    return buf.getvalue()


# ============================
# Styles / layout
# ============================


def _styles() -> Dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()

    title = ParagraphStyle(
        "Title",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        spaceAfter=10,
        textColor=colors.HexColor("#0B1320"),
    )
    subtitle = ParagraphStyle(
        "Subtitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#3A465A"),
        spaceAfter=18,
    )
    h1 = ParagraphStyle(
        "H1",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0B1320"),
        spaceBefore=8,
        spaceAfter=8,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0B1320"),
        spaceBefore=8,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "Body",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=6,
    )
    small = ParagraphStyle(
        "Small",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=4,
    )
    mono = ParagraphStyle(
        "Mono",
        parent=base["Normal"],
        fontName="Courier",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#111827"),
        spaceAfter=6,
    )

    return {
        "title": title,
        "subtitle": subtitle,
        "h1": h1,
        "h2": h2,
        "body": body,
        "small": small,
        "mono": mono,
        "base": base,
    }


def _table_style() -> TableStyle:
    return TableStyle(
        [
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
            ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0B1320")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF2FF")),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D1D5DB")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )


def _draw_header_footer(c, doc, cfg: ReportConfig, first_page: bool) -> None:
    w, h = A4
    c.saveState()

    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#6B7280"))
    c.drawString(2.0 * cm, 1.2 * cm, "Barzel Analytics")
    c.drawRightString(w - 2.0 * cm, 1.2 * cm, f"Page {doc.page}")

    # Header (skip cover)
    if not first_page:
        c.setStrokeColor(colors.HexColor("#E5E7EB"))
        c.setLineWidth(0.6)
        c.line(2.0 * cm, h - 1.65 * cm, w - 2.0 * cm, h - 1.65 * cm)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#0B1320"))
        c.drawString(2.0 * cm, h - 1.35 * cm, cfg.report_title)

    c.restoreState()


# ============================
# Content blocks
# ============================


def _cover(cfg: ReportConfig, styles: Dict[str, ParagraphStyle]):
    now = datetime.now().strftime("%Y-%m-%d")
    districts = ", ".join(cfg.districts) if cfg.districts else "All districts"

    return [
        Spacer(1, 2.2 * cm),
        Paragraph(cfg.report_title, styles["title"]),
        Paragraph(cfg.subtitle, styles["subtitle"]),
        Spacer(1, 0.6 * cm),
        Paragraph(f"<b>Investor profile:</b> {cfg.investor_profile}", styles["body"]),
        Paragraph(f"<b>Districts:</b> {districts}", styles["body"]),
        Paragraph(f"<b>Date:</b> {now}", styles["body"]),
        Spacer(1, 0.8 * cm),
        Paragraph(
            "This report provides a structured market review, a transparent scoring methodology, "
            "and decision support based on the selected districts.",
            styles["body"],
        ),
        Spacer(1, 0.5 * cm),
        Paragraph("<font color='#6B7280'>Confidential - prepared for client use.</font>", styles["small"]),
    ]


def _toc(cfg: ReportConfig, styles: Dict[str, ParagraphStyle]):
    items = [
        "A. Market situation (Understand)",
        "B. District profiles",
        "C. Cross-district comparison (facts)",
        "D. Scoring (methodology + detailed calculations)",
        "E. Decision support",
        "Appendix",
    ]
    district_lines = [f"- District profile: {d}" for d in cfg.districts]
    return [
        Paragraph("Table of contents", styles["h1"]),
        Spacer(1, 0.2 * cm),
        *[Paragraph(f"• {x}", styles["body"]) for x in items],
        Spacer(1, 0.35 * cm),
        Paragraph("Districts included", styles["h2"]),
        *[Paragraph(x, styles["body"]) for x in district_lines],
    ]


def _section_header(title: str, styles: Dict[str, ParagraphStyle]):
    return [Paragraph(title, styles["h1"]), Spacer(1, 0.2 * cm)]


def _executive_overview(df_view: pd.DataFrame, cfg: ReportConfig, styles: Dict[str, ParagraphStyle]):
    snap = snapshot(df_view)

    bullets = [
        f"Scope size: <b>{_fmt(snap.get('n_obs'), 'int')}</b> listings in the current selection.",
        f"Pricing level: median <b>{_fmt(snap.get('median_price_sqm'), 'int')}</b> AED/sqm.",
        f"Liquidity: median time-to-exit <b>{_fmt(snap.get('median_dom'), 'int')}</b> days.",
        f"Income: median net yield <b>{_fmt(snap.get('net_yield_median'), 'pct')}</b>.",
    ]

    return [
        Paragraph("Executive overview (no decision)", styles["h2"]),
        Paragraph(
            "This section summarizes the current market situation for the selected districts. "
            "It is descriptive: it establishes the baseline before introducing any scoring.",
            styles["body"],
        ),
        Spacer(1, 0.1 * cm),
        *[Paragraph(f"• {b}", styles["body"]) for b in bullets],
        Spacer(1, 0.25 * cm),
    ]


def _scope_and_data_quality(df_view: pd.DataFrame, cfg: ReportConfig, styles: Dict[str, ParagraphStyle]):
    def cov(col: str) -> str:
        if col not in df_view.columns or len(df_view) == 0:
            return "n/a"
        return f"{pd.to_numeric(df_view[col], errors='coerce').notna().mean():.0%}"

    rows = [
        ["Dataset rows", f"{len(df_view):,}"],
        ["Districts", ", ".join(cfg.districts) if cfg.districts else "All"],
        ["Coverage: price_per_sqm", cov("price_per_sqm")],
        ["Coverage: days_on_market", cov("days_on_market")],
        ["Coverage: net_yield", cov("net_yield")],
        ["Coverage: service_charge_psm_year", cov("service_charge_psm_year")],
    ]
    t = Table([["Item", "Value"], *rows], colWidths=[7.5 * cm, 7.5 * cm])
    t.setStyle(_table_style())

    return [
        Paragraph("Scope and data quality", styles["h2"]),
        Paragraph(
            "We review coverage and completeness to ensure the descriptive statistics and the scoring are based "
            "on a consistent data foundation.",
            styles["body"],
        ),
        Spacer(1, 0.2 * cm),
        t,
        Spacer(1, 0.25 * cm),
        Paragraph(
            "<font color='#6B7280'>Note: metrics are computed on available non-null values; coverage reflects the share of usable rows per KPI.</font>",
            styles["small"],
        ),
        Spacer(1, 0.25 * cm),
    ]


def _kpi_glossary(styles: Dict[str, ParagraphStyle]):
    rows = [
        ["price_per_sqm", "AED per square meter; pricing level."],
        ["days_on_market", "Number of days the listing stayed active; liquidity / exit speed."],
        ["net_yield", "Net income yield (%, after cost estimates); income efficiency."],
        ["vacancy_days", "Estimated vacancy days; income drag / stability."],
        ["service_charge_psm_year", "Annual service charges per sqm; cost friction."],
    ]
    t = Table([["KPI", "Meaning (simple)"], *rows], colWidths=[5.0 * cm, 10.0 * cm])
    t.setStyle(_table_style())
    return [
        Paragraph("KPI glossary (simple definitions)", styles["h2"]),
        Paragraph(
            "The report uses a consistent KPI set across districts. Definitions are intentionally short; "
            "detailed scoring calculations are provided later.",
            styles["body"],
        ),
        Spacer(1, 0.2 * cm),
        t,
        Spacer(1, 0.4 * cm),
    ]


def _market_overview(df_view: pd.DataFrame, styles: Dict[str, ParagraphStyle]):
    snap = snapshot(df_view)

    rows = [
        ["Listings (n)", _fmt(snap.get("n_obs"), "int")],
        ["Median AED/sqm", _fmt(snap.get("median_price_sqm"), "int")],
        ["P25 / P75 AED/sqm", f"{_fmt(snap.get('p25_price_sqm'), 'int')} / {_fmt(snap.get('p75_price_sqm'), 'int')}"],
        ["Median Days on Market", _fmt(snap.get("median_dom"), "int")],
        ["P25 / P75 DOM", f"{_fmt(snap.get('p25_dom'), 'int')} / {_fmt(snap.get('p75_dom'), 'int')}"],
        ["Median Net Yield", _fmt(snap.get("net_yield_median"), "pct")],
        ["Median Vacancy Days", _fmt(snap.get("vacancy_days_median"), "int")],
        ["Median Service Charge (AED/sqm/year)", _fmt(snap.get("service_charge_median"), "int")],
    ]
    t = Table([["Market metric", "Value"], *rows], colWidths=[7.0 * cm, 8.0 * cm])
    t.setStyle(_table_style())

    takeaways = [
        "Pricing, liquidity, and yield are reported as medians to reduce the impact of outliers.",
        "Quartiles (P25/P75) provide the dispersion band and help interpret heterogeneity.",
        "District-level pages break down these same metrics consistently.",
    ]

    return [
        Paragraph("Market overview (facts)", styles["h2"]),
        Paragraph(
            "This section summarizes the distribution of key metrics for the selected scope. "
            "It is a descriptive baseline before comparing districts and introducing scoring.",
            styles["body"],
        ),
        Spacer(1, 0.2 * cm),
        t,
        Spacer(1, 0.25 * cm),
        Paragraph("Key takeaways", styles["h2"]),
        *[Paragraph(f"• {x}", styles["body"]) for x in takeaways],
    ]


def _district_profile(district: str, df_d: pd.DataFrame, styles: Dict[str, ParagraphStyle]):
    snap = snapshot(df_d)

    rows = [
        ["Listings (n)", _fmt(snap.get("n_obs"), "int")],
        ["Median AED/sqm", _fmt(snap.get("median_price_sqm"), "int")],
        ["P25 / P75 AED/sqm", f"{_fmt(snap.get('p25_price_sqm'), 'int')} / {_fmt(snap.get('p75_price_sqm'), 'int')}"],
        ["Median DOM", _fmt(snap.get("median_dom"), "int")],
        ["Fast-sale <=30d", _fmt(snap.get("fast_sale_ratio_30d"), "ratio")],
        ["Fast-sale <=60d", _fmt(snap.get("fast_sale_ratio_60d"), "ratio")],
        ["Median Net Yield", _fmt(snap.get("net_yield_median"), "pct")],
        ["Median Vacancy Days", _fmt(snap.get("vacancy_days_median"), "int")],
        ["Median Service Charge", _fmt(snap.get("service_charge_median"), "int")],
    ]
    t = Table([["District metric", "Value"], *rows], colWidths=[7.0 * cm, 8.0 * cm])
    t.setStyle(_table_style())

    reading = [
        "Pricing and dispersion indicate the market level and heterogeneity of available listings.",
        "Liquidity is captured by DOM and fast-sale ratios; lower DOM indicates faster exits.",
        "Yield should be interpreted together with service charges and vacancy drag.",
    ]

    return [
        Paragraph(f"District profile: {district}", styles["h2"]),
        Paragraph(
            "This page provides a consistent district-level summary. The goal is clarity: "
            "what is the price level, how quickly assets exit, and what income efficiency looks like.",
            styles["body"],
        ),
        Spacer(1, 0.15 * cm),
        t,
        Spacer(1, 0.25 * cm),
        Paragraph("Key takeaways", styles["h2"]),
        *[Paragraph(f"• {x}", styles["body"]) for x in reading],
    ]


def _comparison_facts(df_view: pd.DataFrame, styles: Dict[str, ParagraphStyle]):
    if "district" not in df_view.columns:
        return [Paragraph("No district column available for comparison.", styles["body"])]

    g = snapshots_by(df_view, "district")
    if g.empty:
        return [Paragraph("Not enough data to build a cross-district table.", styles["body"])]

    cols = [
        ("district", "District"),
        ("n_obs", "n"),
        ("median_price_sqm", "Median AED/sqm"),
        ("median_dom", "Median DOM"),
        ("net_yield_median", "Net yield (median)"),
        ("service_charge_median", "Service charge (median)"),
    ]

    view_cols = [c for c, _ in cols if c in g.columns]
    data = [[label for c, label in cols if c in g.columns]]

    for _, r in g.sort_values("n_obs", ascending=False).iterrows():
        row = []
        for c in view_cols:
            if c == "district":
                row.append(str(r[c]))
            elif "yield" in c:
                row.append(_fmt(r[c], "pct"))
            elif c == "n_obs":
                row.append(_fmt(r[c], "int"))
            else:
                row.append(_fmt(r[c], "int"))
        data.append(row)

    t = Table(data, colWidths=[4.0 * cm] + [2.2 * cm] * (len(data[0]) - 1))
    t.setStyle(_table_style())

    return [
        Paragraph("Comparison table (facts, before scoring)", styles["h2"]),
        Paragraph(
            "This table compares districts using raw descriptive metrics only. "
            "Scoring is introduced in the next section with a transparent methodology.",
            styles["body"],
        ),
        Spacer(1, 0.2 * cm),
        t,
        Spacer(1, 0.25 * cm),
    ]


def _scoring_methodology(cfg: ReportConfig, styles: Dict[str, ParagraphStyle]):
    rows = [
        ["Liquidity", "Exit speed and market depth", "Lower DOM and lower vacancy are better"],
        ["Yield", "Income efficiency", "Higher net yield is better"],
        ["Risk", "Pricing dispersion / volatility", "Lower dispersion is better"],
        ["Trend", "Price dynamics over time", "Higher momentum is better"],
    ]
    t = Table([["Pillar", "Meaning", "Direction"], *rows], colWidths=[2.6 * cm, 7.0 * cm, 5.4 * cm])
    t.setStyle(_table_style())

    return [
        Paragraph("Scoring overview", styles["h2"]),
        Paragraph(
            "Scores translate heterogeneous metrics into a comparable 0-100 scale. "
            "Each pillar is computed on 0-25, and the total score is the sum (0-100).",
            styles["body"],
        ),
        Spacer(1, 0.15 * cm),
        t,
        Spacer(1, 0.25 * cm),
        Paragraph("Normalization principle", styles["h2"]),
        Paragraph(
            "For each KPI, we compute the district value (typically a median) and locate it within the "
            "market-wide distribution. This location is converted to a percentile (0-1), then scaled to points.",
            styles["body"],
        ),
        Paragraph("<font name='Courier'>percentile = share of market values <= district_value</font>", styles["mono"]),
        Paragraph("If lower is better (e.g., DOM), we invert as <font name='Courier'>1 - percentile</font>.", styles["body"]),
        Spacer(1, 0.2 * cm),
    ]


def _scoring_details(df_all: pd.DataFrame, df_ex: pd.DataFrame, district_name: str, styles: Dict[str, ParagraphStyle]):
    det = barzel_score_details(df_all=df_all, df_view=df_ex)

    lines = [
        f"Example district: <b>{district_name}</b>",
        f"District medians: price_per_sqm={_fmt(det['inputs']['price_median'], 'int')}, "
        f"DOM={_fmt(det['inputs']['dom_median'], 'int')}, net_yield={_fmt(det['inputs']['net_yield_median'], 'pct')}, "
        f"vacancy_days={_fmt(det['inputs']['vacancy_median'], 'int')}",
        f"Market sample sizes used: price={det['n_all']['price']}, DOM={det['n_all']['dom']}, "
        f"yield={det['n_all']['yield']}, vacancy={det['n_all']['vacancy']}",
    ]

    data = [["Pillar", "KPI", "Percentile (0-1)", "Points (0-25)"]]
    for row in det["rows"]:
        data.append(
            [
                row["pillar"],
                row["kpi"],
                f"{row['pct']:.3f}" if row["pct"] == row["pct"] else "n/a",
                f"{row['points']:.2f}" if row["points"] == row["points"] else "n/a",
            ]
        )
    t = Table(data, colWidths=[2.8 * cm, 6.2 * cm, 3.3 * cm, 3.0 * cm])
    t.setStyle(_table_style())

    totals = det["totals"]
    totals_table = Table(
        [
            ["Liquidity", "Yield", "Risk", "Trend", "Total"],
            [
                _fmt(totals.get("Liquidity"), "float"),
                _fmt(totals.get("Yield"), "float"),
                _fmt(totals.get("Risk"), "float"),
                _fmt(totals.get("Trend"), "float"),
                _fmt(totals.get("Total"), "float"),
            ],
        ],
        colWidths=[3.0 * cm, 3.0 * cm, 3.0 * cm, 3.0 * cm, 3.0 * cm],
    )
    totals_table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
                ("FONT", (0, 1), (-1, 1), "Helvetica-Bold", 10),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF2FF")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D1D5DB")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    return [
        Paragraph("Worked example: detailed scoring calculations", styles["h2"]),
        Paragraph(
            "This example shows the exact steps used to compute pillar scores. "
            "Percentiles are computed from the market-wide distribution; points are derived by scaling to 0-25.",
            styles["body"],
        ),
        Spacer(1, 0.1 * cm),
        *[Paragraph(f"• {x}", styles["body"]) for x in lines],
        Spacer(1, 0.15 * cm),
        t,
        Spacer(1, 0.25 * cm),
        Paragraph("Score summary (example district)", styles["h2"]),
        totals_table,
        Spacer(1, 0.25 * cm),
        Paragraph(
            "Interpretation: higher pillar points indicate stronger relative positioning on that dimension. "
            "The total score is the sum of pillars and supports cross-district comparison.",
            styles["body"],
        ),
        Spacer(1, 0.3 * cm),
    ]


def _scoring_results(df_all: pd.DataFrame, df_view: pd.DataFrame, cfg: ReportConfig, styles: Dict[str, ParagraphStyle]):
    if "district" not in df_view.columns:
        return [Paragraph("No district column available to compute score results.", styles["body"])]

    scores = barzel_scores_by_district(df_all=df_all, df_view=df_view, districts=cfg.districts)
    if scores.empty:
        return [Paragraph("Not enough data to compute district scores.", styles["body"])]

    scores = scores.sort_values("Total", ascending=False)

    data = [["District", "Liquidity", "Yield", "Risk", "Trend", "Total"]]
    for _, r in scores.iterrows():
        data.append(
            [
                str(r["district"]),
                _fmt(r["Liquidity"], "float"),
                _fmt(r["Yield"], "float"),
                _fmt(r["Risk"], "float"),
                _fmt(r["Trend"], "float"),
                _fmt(r["Total"], "float"),
            ]
        )
    t = Table(data, colWidths=[4.0 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm])
    t.setStyle(_table_style())

    top = scores.iloc[0]["district"]
    second = scores.iloc[1]["district"] if len(scores) > 1 else None

    bullets = [f"Top-ranked district by total score: <b>{top}</b>."]
    if second is not None:
        bullets.append(f"Second-ranked district: <b>{second}</b>.")
    bullets.append("Interpretation and action steps are provided in the Decision support section.")

    return [
        Paragraph("District score results", styles["h2"]),
        Paragraph("This table consolidates pillar scores for each district.", styles["body"]),
        Spacer(1, 0.2 * cm),
        t,
        Spacer(1, 0.25 * cm),
        Paragraph("Key observations", styles["h2"]),
        *[Paragraph(f"• {b}", styles["body"]) for b in bullets],
    ]


def _decision_support(df_all: pd.DataFrame, df_view: pd.DataFrame, cfg: ReportConfig, styles: Dict[str, ParagraphStyle]):
    if "district" not in df_view.columns:
        return [Paragraph("Decision support requires a district selection.", styles["body"])]

    scores = barzel_scores_by_district(df_all=df_all, df_view=df_view, districts=cfg.districts)
    if scores.empty:
        return [Paragraph("Not enough data to produce decision support.", styles["body"])]

    scores = scores.sort_values("Total", ascending=False)
    leader = scores.iloc[0]
    laggard = scores.iloc[-1]

    bullets = [
        f"The scoring indicates strongest overall positioning for <b>{leader['district']}</b> (Total: {_fmt(leader['Total'], 'float')}).",
        f"The weakest overall positioning in scope is <b>{laggard['district']}</b> (Total: {_fmt(laggard['Total'], 'float')}).",
        "Use pillar-by-pillar differences to understand the trade-offs (liquidity vs yield vs risk vs trend).",
    ]

    blocks = [
        Paragraph("Interpretation (what the ranking means)", styles["h2"]),
        Paragraph(
            "This section translates scoring outcomes into a structured reading grounded in the metrics and the methodology.",
            styles["body"],
        ),
        Spacer(1, 0.1 * cm),
        *[Paragraph(f"• {b}", styles["body"]) for b in bullets],
        Spacer(1, 0.25 * cm),
    ]

    if cfg.notes.strip():
        blocks += [
            Paragraph("Client / analyst notes", styles["h2"]),
            Paragraph(_escape(cfg.notes).replace("\n", "<br/>"), styles["body"]),
            Spacer(1, 0.25 * cm),
        ]

    return blocks


def _action_plan(df_all: pd.DataFrame, df_view: pd.DataFrame, cfg: ReportConfig, styles: Dict[str, ParagraphStyle]):
    top = "Top district"
    if "district" in df_view.columns:
        scores = barzel_scores_by_district(df_all=df_all, df_view=df_view, districts=cfg.districts)
        if not scores.empty:
            top = scores.sort_values("Total", ascending=False).iloc[0]["district"]

    steps = [
        f"Focus sourcing and shortlist building on <b>{top}</b> as a priority target within the selected strategy.",
        "Narrow to 1-2 asset types (e.g., Studio / 1BR / 2BR) to improve comparability and reduce dispersion.",
        "Apply guardrails on pricing level (AED/sqm band) and time-to-exit (DOM) consistent with liquidity targets.",
        "Validate the cost stack (service charges) and vacancy assumptions before final underwriting.",
        "Use a weekly refresh to monitor momentum (trend pillar) and detect changes in market conditions.",
    ]

    return [
        Paragraph("Action plan (what to do next)", styles["h2"]),
        Paragraph("Concrete execution steps translating analytics into actions.", styles["body"]),
        Spacer(1, 0.1 * cm),
        *[Paragraph(f"{i+1}) {s}", styles["body"]) for i, s in enumerate(steps)],
        Spacer(1, 0.25 * cm),
    ]


def _appendix_tables(df_view: pd.DataFrame, styles: Dict[str, ParagraphStyle]):
    blocks = [
        Paragraph("District appendix table", styles["h2"]),
        Paragraph("Compact district table for reference.", styles["body"]),
        Spacer(1, 0.2 * cm),
    ]

    if "district" not in df_view.columns:
        blocks.append(Paragraph("No district column available.", styles["body"]))
        return blocks

    g = snapshots_by(df_view, "district")
    if g.empty:
        blocks.append(Paragraph("Not enough data for district appendix.", styles["body"]))
        return blocks

    g = g.sort_values("n_obs", ascending=False)
    data = [["District", "n", "Median AED/sqm", "Median DOM", "Net yield"]]
    for _, r in g.iterrows():
        data.append(
            [
                str(r.get("district")),
                _fmt(r.get("n_obs"), "int"),
                _fmt(r.get("median_price_sqm"), "int"),
                _fmt(r.get("median_dom"), "int"),
                _fmt(r.get("net_yield_median"), "pct"),
            ]
        )

    t = Table(data, colWidths=[5.0 * cm, 2.0 * cm, 3.2 * cm, 3.0 * cm, 2.8 * cm])
    t.setStyle(_table_style())
    blocks.append(t)
    return blocks


# ============================
# Formatting utils
# ============================


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fmt(x, kind: str = "float") -> str:
    if x is None:
        return "n/a"
    try:
        if x != x:
            return "n/a"
    except Exception:
        pass

    if kind == "int":
        try:
            return f"{int(round(float(x))):,}"
        except Exception:
            return "n/a"

    if kind == "pct":
        try:
            return f"{float(x):.2f}%"
        except Exception:
            return "n/a"

    if kind == "ratio":
        try:
            return f"{float(x):.0%}"
        except Exception:
            return "n/a"

    try:
        return f"{float(x):.2f}"
    except Exception:
        return "n/a"
