import numpy as np
import pandas as pd


def _num(s):
    return pd.to_numeric(s, errors="coerce")


def price_consistency_index(df: pd.DataFrame) -> float:
    """
    Coefficient of variation of price_per_sqm.
    Lower = more consistent.
    """
    p = _num(df.get("price_per_sqm"))
    p = p.dropna()
    if len(p) < 10:
        return np.nan
    m = p.mean()
    if m <= 0:
        return np.nan
    return float(p.std() / m)


def intra_building_dispersion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Dispersion of price_per_sqm within each building.
    """
    if "building_name" not in df.columns:
        return pd.DataFrame()
    d = df.dropna(subset=["building_name", "price_per_sqm"])
    if d.empty:
        return pd.DataFrame()
    out = (
        d.groupby("building_name")
        .agg(
            n_obs=("price_per_sqm", "size"),
            median_price_sqm=("price_per_sqm", "median"),
            std_price_sqm=("price_per_sqm", "std"),
        )
        .reset_index()
    )
    out["cv_price"] = out["std_price_sqm"] / out["median_price_sqm"]
    return out.sort_values(["n_obs", "cv_price"], ascending=[False, True])


def liquidity_depth_ratio(df: pd.DataFrame) -> float:
    """
    Proxy: listings_count / median_DOM
    Higher = deeper liquidity.
    """
    dom = _num(df.get("days_on_market"))
    dom_med = float(dom.median()) if dom.notna().any() else np.nan
    n = len(df)
    if not np.isfinite(dom_med) or dom_med <= 0:
        return np.nan
    return float(n / dom_med)


def yield_efficiency_ratio(df: pd.DataFrame) -> float:
    """
    net_yield / price volatility (std of price_per_sqm)
    Higher = better yield per unit of volatility.
    """
    net = _num(df.get("net_yield")).dropna()
    p = _num(df.get("price_per_sqm")).dropna()
    if len(net) < 10 or len(p) < 10:
        return np.nan
    vol = float(p.std())
    if vol <= 0:
        return np.nan
    return float(net.median() / vol)


def vacancy_drag_index(df: pd.DataFrame) -> float:
    """
    gross_yield - net_yield (median)
    Higher = more drag (worse).
    """
    g = _num(df.get("gross_yield"))
    n = _num(df.get("net_yield"))
    d = (g - n).dropna()
    return float(d.median()) if len(d) else np.nan


def cost_to_yield_ratio(df: pd.DataFrame) -> float:
    """
    service_charge_psm_year / (net_yield) scaled to be readable.
    Not perfect economics, but detects 'high costs vs return' pockets.
    """
    sc = _num(df.get("service_charge_psm_year")).dropna()
    net = _num(df.get("net_yield")).dropna()
    if len(sc) < 10 or len(net) < 10:
        return np.nan
    net_med = float(net.median())
    if net_med == 0 or not np.isfinite(net_med):
        return np.nan
    return float(sc.median() / abs(net_med))


def typology_concentration(df: pd.DataFrame) -> pd.DataFrame:
    """
    Share by bedrooms (or property_type fallback).
    """
    if "bedrooms" in df.columns:
        s = df["bedrooms"]
        out = s.value_counts(dropna=False).reset_index()
        out.columns = ["bedrooms", "count"]
    else:
        out = df["property_type"].value_counts(dropna=False).reset_index()
        out.columns = ["bedrooms", "count"]
    out["share"] = out["count"] / out["count"].sum()
    return out


def terrace_premium(df: pd.DataFrame) -> dict:
    """
    Premium in price_per_sqm for has_terrace True vs False.
    """
    if "has_terrace" not in df.columns:
        return {"premium_abs": np.nan, "premium_pct": np.nan}
    d = df.dropna(subset=["price_per_sqm", "has_terrace"]).copy()
    if len(d) < 20:
        return {"premium_abs": np.nan, "premium_pct": np.nan}
    a = d[d["has_terrace"] == True]["price_per_sqm"].median()
    b = d[d["has_terrace"] == False]["price_per_sqm"].median()
    if not np.isfinite(a) or not np.isfinite(b) or b == 0:
        return {"premium_abs": np.nan, "premium_pct": np.nan}
    return {"premium_abs": float(a - b), "premium_pct": float((a - b) / b)}
