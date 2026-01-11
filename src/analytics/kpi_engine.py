import numpy as np
import pandas as pd


def weighted_median(values: pd.Series, weights: pd.Series) -> float:
    v = pd.to_numeric(values, errors="coerce")
    w = pd.to_numeric(weights, errors="coerce")
    mask = v.notna() & w.notna() & (w > 0)
    v, w = v[mask], w[mask]
    if len(v) == 0:
        return np.nan
    order = np.argsort(v.values)
    v_sorted = v.values[order]
    w_sorted = w.values[order]
    csum = np.cumsum(w_sorted)
    cutoff = w_sorted.sum() / 2.0
    return float(v_sorted[np.searchsorted(csum, cutoff)])


# -------------------------
# KPI blocks
# -------------------------

def kpi_pricing(df: pd.DataFrame) -> dict:
    s = pd.to_numeric(df.get("price_per_sqm"), errors="coerce")
    return {
        "median_price_sqm": float(s.median()) if s.notna().any() else np.nan,
        "p25_price_sqm": float(s.quantile(0.25)) if s.notna().any() else np.nan,
        "p75_price_sqm": float(s.quantile(0.75)) if s.notna().any() else np.nan,
        "price_dispersion_std": float(s.std()) if s.notna().any() else np.nan,
    }


def kpi_liquidity(df: pd.DataFrame) -> dict:
    dom = pd.to_numeric(df.get("days_on_market"), errors="coerce")
    out = {
        "median_dom": float(dom.median()) if dom.notna().any() else np.nan,
        "p25_dom": float(dom.quantile(0.25)) if dom.notna().any() else np.nan,
        "p75_dom": float(dom.quantile(0.75)) if dom.notna().any() else np.nan,
        "fast_sale_ratio_30d": float((dom <= 30).mean()) if len(dom) else np.nan,
        "fast_sale_ratio_60d": float((dom <= 60).mean()) if len(dom) else np.nan,
    }
    # pricing discipline
    p = pd.to_numeric(df.get("price_per_sqm"), errors="coerce")
    clean = pd.DataFrame({"p": p, "dom": dom}).dropna()
    out["overpricing_penalty_corr"] = float(clean["p"].corr(clean["dom"])) if len(clean) >= 10 else np.nan
    return out


def kpi_yield(df: pd.DataFrame) -> dict:
    gross = pd.to_numeric(df.get("gross_yield"), errors="coerce")
    net = pd.to_numeric(df.get("net_yield"), errors="coerce")
    vac = pd.to_numeric(df.get("vacancy_days"), errors="coerce")

    return {
        "gross_yield_median": float(gross.median()) if gross.notna().any() else np.nan,
        "net_yield_median": float(net.median()) if net.notna().any() else np.nan,
        "net_yield_dispersion_std": float(net.std()) if net.notna().any() else np.nan,
        "vacancy_days_median": float(vac.median()) if vac.notna().any() else np.nan,
        "vacancy_drag_median": float((gross - net).median()) if gross.notna().any() and net.notna().any() else np.nan,
    }


def kpi_costs(df: pd.DataFrame) -> dict:
    sc = pd.to_numeric(df.get("service_charge_psm_year"), errors="coerce")
    return {
        "service_charge_median": float(sc.median()) if sc.notna().any() else np.nan,
        "service_charge_dispersion_std": float(sc.std()) if sc.notna().any() else np.nan,
    }


def kpi_terrace(df: pd.DataFrame) -> dict:
    ht = df.get("has_terrace")
    ts = pd.to_numeric(df.get("terrace_size_sqm"), errors="coerce")

    terrace_rate = np.nan
    if ht is not None:
        try:
            terrace_rate = float(pd.Series(ht).dropna().astype(bool).mean())
        except Exception:
            terrace_rate = np.nan

    return {
        "terrace_rate": terrace_rate,
        "terrace_size_median": float(ts.median()) if ts.notna().any() else np.nan,
    }

def floor_weighted_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a floor-bucketed (market-realistic) weighted median AED/sqm.
    Keeps everything else unchanged.
    """
    required = {"floor", "price_per_sqm", "size_sqm"}
    if not required.issubset(df.columns):
        return pd.DataFrame(columns=["floor_bucket", "weighted_price_sqm"])

    d = df.dropna(subset=["floor", "price_per_sqm", "size_sqm"]).copy()
    d["floor"] = pd.to_numeric(d["floor"], errors="coerce")
    d["price_per_sqm"] = pd.to_numeric(d["price_per_sqm"], errors="coerce")
    d["size_sqm"] = pd.to_numeric(d["size_sqm"], errors="coerce")

    d = d.dropna(subset=["floor", "price_per_sqm", "size_sqm"])
    d = d[(d["size_sqm"] > 0) & (d["price_per_sqm"] > 0)]
    if d.empty:
        return pd.DataFrame(columns=["floor_bucket", "weighted_price_sqm"])

    # ---- Floor buckets (market reality > per-floor micro-noise)
    def _bucket(f: float) -> str:
        try:
            f = float(f)
        except Exception:
            return "Unknown"
        if f <= 5:
            return "1–5"
        if f <= 10:
            return "6–10"
        if f <= 20:
            return "11–20"
        if f <= 30:
            return "21–30"
        if f <= 40:
            return "31–40"
        if f <= 50:
            return "41–50"
        return "50+"

    d["floor_bucket"] = d["floor"].apply(_bucket)

    order = ["1–5", "6–10", "11–20", "21–30", "31–40", "41–50", "50+"]
    d["floor_bucket"] = pd.Categorical(d["floor_bucket"], categories=order, ordered=True)

    res = (
        d.groupby("floor_bucket", dropna=True)
        .apply(lambda x: weighted_median(x["price_per_sqm"], x["size_sqm"]))
        .reset_index(name="weighted_price_sqm")
        .sort_values("floor_bucket")
    )
    return res

def price_timeseries_proxy(df: pd.DataFrame, date_col: str = "first_seen") -> pd.DataFrame:
    if date_col not in df.columns or "price_per_sqm" not in df.columns:
        return pd.DataFrame(columns=["month", "median_price_sqm"])
    d = df.dropna(subset=[date_col, "price_per_sqm"]).copy()
    if d.empty:
        return pd.DataFrame(columns=["month", "median_price_sqm"])
    d["month"] = pd.to_datetime(d[date_col], utc=True).dt.to_period("M").dt.to_timestamp()
    out = d.groupby("month")["price_per_sqm"].median().reset_index(name="median_price_sqm").sort_values("month")
    return out
