import numpy as np
import pandas as pd


def _clip01(x: float) -> float:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return np.nan
    return float(max(0.0, min(1.0, x)))


def percentile_score(series: pd.Series, value: float, higher_is_better: bool = True) -> float:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 10 or value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    pct = float((s <= value).mean())
    return _clip01(pct if higher_is_better else 1.0 - pct)


def barzel_score_pdf_only(df_all: pd.DataFrame, df_view: pd.DataFrame) -> dict:
    """
    Scores are computed only for PDF.
    Each pillar is 0-25, total 0-100.
    """

    # Core series (market distribution across all data)
    p_all = df_all.get("price_per_sqm")
    dom_all = df_all.get("days_on_market")
    net_all = df_all.get("net_yield")
    vac_all = df_all.get("vacancy_days")

    # View values (medians)
    p = pd.to_numeric(df_view.get("price_per_sqm"), errors="coerce").median()
    dom = pd.to_numeric(df_view.get("days_on_market"), errors="coerce").median()
    net = pd.to_numeric(df_view.get("net_yield"), errors="coerce").median()
    vac = pd.to_numeric(df_view.get("vacancy_days"), errors="coerce").median()

    # Liquidity: low DOM is better
    s_dom = percentile_score(pd.Series(dom_all), dom, higher_is_better=False)

    # Yield: higher is better
    s_yield = percentile_score(pd.Series(net_all), net, higher_is_better=True)

    # Risk proxy: volatility of price_per_sqm in view (lower is better)
    vol_view = pd.to_numeric(df_view.get("price_per_sqm"), errors="coerce").std()
    vol_all = pd.to_numeric(df_all.get("price_per_sqm"), errors="coerce").groupby(df_all.get("district")).std()
    s_risk = percentile_score(pd.Series(vol_all), vol_view, higher_is_better=False)

    # Trend proxy: price momentum from first_seen (higher is better)
    trend = np.nan
    if "first_seen" in df_view.columns and "price_per_sqm" in df_view.columns:
        d = df_view.dropna(subset=["first_seen", "price_per_sqm"]).copy()
        if len(d) >= 30:
            d["month"] = pd.to_datetime(d["first_seen"], utc=True).dt.to_period("M").dt.to_timestamp()
            g = d.groupby("month")["price_per_sqm"].median().sort_index()
            if len(g) >= 6:
                trend = float((g.iloc[-1] - g.iloc[0]) / g.iloc[0])

    trend_dist = []
    if "first_seen" in df_all.columns and "price_per_sqm" in df_all.columns and "district" in df_all.columns:
        for _, sub in df_all.dropna(subset=["district"]).groupby("district"):
            dd = sub.dropna(subset=["first_seen", "price_per_sqm"]).copy()
            if len(dd) < 30:
                continue
            dd["month"] = pd.to_datetime(dd["first_seen"], utc=True).dt.to_period("M").dt.to_timestamp()
            gg = dd.groupby("month")["price_per_sqm"].median().sort_index()
            if len(gg) >= 6 and gg.iloc[0] > 0:
                trend_dist.append(float((gg.iloc[-1] - gg.iloc[0]) / gg.iloc[0]))

    s_trend = percentile_score(pd.Series(trend_dist), trend, higher_is_better=True) if len(trend_dist) else np.nan

    # Optional: vacancy (lower is better) blended into liquidity a bit
    s_vac = percentile_score(pd.Series(vac_all), vac, higher_is_better=False)

    # Pillars (0-25)
    liquidity = 25.0 * np.nanmean([s_dom, s_vac])
    yield_ = 25.0 * s_yield
    risk = 25.0 * s_risk
    trend_ = 25.0 * s_trend

    total = float(np.nansum([liquidity, yield_, risk, trend_]))

    return {
        "Liquidity": liquidity,
        "Yield": yield_,
        "Risk": risk,
        "Trend": trend_,
        "Total": total,
    }


def barzel_score_details(df_all: pd.DataFrame, df_view: pd.DataFrame) -> dict:
    """
    Transparent breakdown used by the PDF:
    - inputs (medians)
    - n_all (market sample sizes)
    - rows (per-KPI percentile + points)
    - totals (pillars + total)
    """

    p_all = pd.to_numeric(df_all.get("price_per_sqm"), errors="coerce")
    dom_all = pd.to_numeric(df_all.get("days_on_market"), errors="coerce")
    net_all = pd.to_numeric(df_all.get("net_yield"), errors="coerce")
    vac_all = pd.to_numeric(df_all.get("vacancy_days"), errors="coerce")

    p = pd.to_numeric(df_view.get("price_per_sqm"), errors="coerce").median()
    dom = pd.to_numeric(df_view.get("days_on_market"), errors="coerce").median()
    net = pd.to_numeric(df_view.get("net_yield"), errors="coerce").median()
    vac = pd.to_numeric(df_view.get("vacancy_days"), errors="coerce").median()

    pct_dom = percentile_score(dom_all.dropna(), dom, higher_is_better=False)
    pct_yield = percentile_score(net_all.dropna(), net, higher_is_better=True)

    vol_view = pd.to_numeric(df_view.get("price_per_sqm"), errors="coerce").std()
    vol_all = pd.to_numeric(df_all.get("price_per_sqm"), errors="coerce").groupby(df_all.get("district")).std()
    pct_risk = percentile_score(pd.Series(vol_all).dropna(), vol_view, higher_is_better=False)

    trend = np.nan
    if "first_seen" in df_view.columns and "price_per_sqm" in df_view.columns:
        d = df_view.dropna(subset=["first_seen", "price_per_sqm"]).copy()
        if len(d) >= 30:
            d["month"] = pd.to_datetime(d["first_seen"], utc=True).dt.to_period("M").dt.to_timestamp()
            g = d.groupby("month")["price_per_sqm"].median().sort_index()
            if len(g) >= 6 and g.iloc[0] > 0:
                trend = float((g.iloc[-1] - g.iloc[0]) / g.iloc[0])

    trend_dist = []
    if "first_seen" in df_all.columns and "price_per_sqm" in df_all.columns and "district" in df_all.columns:
        for _, sub in df_all.dropna(subset=["district"]).groupby("district"):
            dd = sub.dropna(subset=["first_seen", "price_per_sqm"]).copy()
            if len(dd) < 30:
                continue
            dd["month"] = pd.to_datetime(dd["first_seen"], utc=True).dt.to_period("M").dt.to_timestamp()
            gg = dd.groupby("month")["price_per_sqm"].median().sort_index()
            if len(gg) >= 6 and gg.iloc[0] > 0:
                trend_dist.append(float((gg.iloc[-1] - gg.iloc[0]) / gg.iloc[0]))

    pct_trend = percentile_score(pd.Series(trend_dist), trend, higher_is_better=True) if len(trend_dist) else np.nan

    pct_vac = percentile_score(vac_all.dropna(), vac, higher_is_better=False)

    pts_dom = 25.0 * pct_dom if pct_dom == pct_dom else np.nan
    pts_vac = 25.0 * pct_vac if pct_vac == pct_vac else np.nan
    liquidity = float(np.nanmean([pts_dom, pts_vac])) if (pts_dom == pts_dom or pts_vac == pts_vac) else np.nan
    yield_ = 25.0 * pct_yield if pct_yield == pct_yield else np.nan
    risk = 25.0 * pct_risk if pct_risk == pct_risk else np.nan
    trend_ = 25.0 * pct_trend if pct_trend == pct_trend else np.nan
    total = float(np.nansum([liquidity, yield_, risk, trend_]))

    rows = [
        {"pillar": "Liquidity", "kpi": "days_on_market (median)", "pct": pct_dom, "points": pts_dom},
        {"pillar": "Liquidity", "kpi": "vacancy_days (median)", "pct": pct_vac, "points": pts_vac},
        {"pillar": "Yield", "kpi": "net_yield (median)", "pct": pct_yield, "points": yield_},
        {"pillar": "Risk", "kpi": "price_per_sqm dispersion (std)", "pct": pct_risk, "points": risk},
        {"pillar": "Trend", "kpi": "price momentum (6M+)", "pct": pct_trend, "points": trend_},
    ]

    return {
        "inputs": {
            "price_median": p,
            "dom_median": dom,
            "net_yield_median": net,
            "vacancy_median": vac,
            "price_volatility": vol_view,
            "trend": trend,
        },
        "n_all": {
            "price": int(p_all.dropna().shape[0]),
            "dom": int(dom_all.dropna().shape[0]),
            "yield": int(net_all.dropna().shape[0]),
            "vacancy": int(vac_all.dropna().shape[0]),
        },
        "rows": rows,
        "totals": {
            "Liquidity": liquidity,
            "Yield": yield_,
            "Risk": risk,
            "Trend": trend_,
            "Total": total,
        },
    }


def barzel_scores_by_district(df_all: pd.DataFrame, df_view: pd.DataFrame, districts: list[str]) -> pd.DataFrame:
    """Compute pillar scores per district (for PDF tables)."""
    if "district" not in df_view.columns:
        return pd.DataFrame()

    d_list = districts or sorted(df_view["district"].dropna().unique().tolist())
    out = []
    for d in d_list:
        sub = df_view[df_view["district"].astype(str) == str(d)]
        if len(sub) < 10:
            continue
        s = barzel_score_pdf_only(df_all=df_all, df_view=sub)
        out.append({"district": str(d), **s})
    return pd.DataFrame(out)
