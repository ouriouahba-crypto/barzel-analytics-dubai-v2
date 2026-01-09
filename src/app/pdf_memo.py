from __future__ import annotations

import io
from dataclasses import dataclass
from typing import List, Optional

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from src.analytics.market_views import snapshot, snapshots_by
from src.analytics.scoring_pdf_only import barzel_score_pdf_only


@dataclass
class MemoConfig:
    investor_profile: str
    districts: List[str]
    notes: str = ""


def _fmt(x, kind="float"):
    if x is None:
        return "n/a"
    try:
        if x != x:  # NaN
            return "n/a"
    except Exception:
        pass
    if kind == "int":
        return f"{int(x):,}"
    if kind == "pct":
        return f"{float(x):.2f}%"
    return f"{float(x):,.2f}"


def build_pdf_memo(df_all: pd.DataFrame, df_view: pd.DataFrame, cfg: MemoConfig) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    # ----------------
    # Page 1: Cover
    # ----------------
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, h - 2.2 * cm, "Barzel Analytics — Dubai (V2)")
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, h - 3.0 * cm, "Decision memo (scores live only in this PDF)")
    c.drawString(2 * cm, h - 3.6 * cm, f"Investor profile: {cfg.investor_profile}")
    c.drawString(2 * cm, h - 4.2 * cm, f"Scope districts: {', '.join(cfg.districts) if cfg.districts else 'All'}")

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, h - 5.0 * cm, "Notes:")
    text = c.beginText(2 * cm, h - 5.6 * cm)
    text.setFont("Helvetica", 9)
    for line in (cfg.notes or "").splitlines()[:12]:
        text.textLine(line)
    c.drawText(text)

    c.showPage()

    # ----------------
    # Page 2: Summary metrics + scores
    # ----------------
    snap = snapshot(df_view)
    scores = barzel_score_pdf_only(df_all, df_view)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, h - 2.0 * cm, "Executive summary (facts + scores)")

    y = h - 3.2 * cm
    c.setFont("Helvetica", 10)
    lines = [
        f"Listings: {_fmt(snap['n_obs'], 'int')}",
        f"Median AED/sqm: {_fmt(snap['median_price_sqm'], 'int')}",
        f"Median DOM: {_fmt(snap['median_dom'], 'int')}",
        f"Net yield (median): {_fmt(snap['net_yield_median'], 'pct')}",
        f"Vacancy days (median): {_fmt(snap['vacancy_days_median'], 'int')}",
        f"Service charge median (AED/sqm/year): {_fmt(snap['service_charge_median'], 'int')}",
    ]
    for ln in lines:
        c.drawString(2 * cm, y, ln)
        y -= 0.55 * cm

    y -= 0.3 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Barzel Scores (PDF-only)")
    y -= 0.8 * cm

    c.setFont("Helvetica", 10)
    for k in ["Liquidity", "Yield", "Risk", "Trend", "Total"]:
        c.drawString(2 * cm, y, f"{k}: {_fmt(scores.get(k), 'float')}")
        y -= 0.55 * cm

    c.showPage()

    # ----------------
    # Page 3: District table (facts)
    # ----------------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, h - 2.0 * cm, "District appendix (descriptive table)")
    table = snapshots_by(df_view, "district")
    if not table.empty:
        table = table.sort_values("n_obs", ascending=False).head(20)

        y = h - 3.0 * cm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2 * cm, y, "District")
        c.drawString(6 * cm, y, "n")
        c.drawString(8 * cm, y, "Med AED/sqm")
        c.drawString(12 * cm, y, "Med DOM")
        c.drawString(15 * cm, y, "Net Yield")
        y -= 0.6 * cm
        c.setFont("Helvetica", 9)

        for _, r in table.iterrows():
            c.drawString(2 * cm, y, str(r["district"])[:28])
            c.drawString(6 * cm, y, _fmt(r["n_obs"], "int"))
            c.drawString(8 * cm, y, _fmt(r["median_price_sqm"], "int"))
            c.drawString(12 * cm, y, _fmt(r["median_dom"], "int"))
            c.drawString(15 * cm, y, _fmt(r["net_yield_median"], "pct"))
            y -= 0.5 * cm
            if y < 2.0 * cm:
                c.showPage()
                y = h - 2.0 * cm

    c.showPage()

    # (You will extend to 10–20 pages later: risks, scenarios, building shortlist, etc.)
    c.save()
    return buf.getvalue()
