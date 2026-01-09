import numpy as np
import pandas as pd


def _num(s):
    return pd.to_numeric(s, errors="coerce")


def safe_quantiles(s: pd.Series, qs=(0.25, 0.5, 0.75)) -> dict:
    s = _num(s).dropna()
    if len(s) == 0:
        return {f"q{int(q*100)}": np.nan for q in qs}
    return {f"q{int(q*100)}": float(s.quantile(q)) for q in qs}


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    v = _num(values)
    w = _num(weights)
    m = v.notna() & w.notna() & (w > 0)
    v, w = v[m], w[m]
    if len(v) == 0:
        return np.nan
    return float((v * w).sum() / w.sum())


def bucketize(series: pd.Series, bins, labels=None) -> pd.Series:
    s = _num(series)
    return pd.cut(s, bins=bins, labels=labels, include_lowest=True)


def group_stats(
    df: pd.DataFrame,
    group_cols,
    value_col: str,
    weight_col: str | None = None,
    min_n: int = 10,
) -> pd.DataFrame:
    if isinstance(group_cols, str):
        group_cols = [group_cols]
    if any(c not in df.columns for c in group_cols) or value_col not in df.columns:
        return pd.DataFrame()

    d = df.copy()
    d[value_col] = _num(d[value_col])
    d = d.dropna(subset=group_cols + [value_col])
    if d.empty:
        return pd.DataFrame()

    if weight_col and weight_col in d.columns:
        d[weight_col] = _num(d[weight_col])

    rows = []
    for key, sub in d.groupby(group_cols, dropna=True):
        n = int(sub[value_col].notna().sum())
        if n < min_n:
            continue
        q = safe_quantiles(sub[value_col], qs=(0.1, 0.25, 0.5, 0.75, 0.9))
        row = {**{group_cols[i]: key[i] if isinstance(key, tuple) else key for i in range(len(group_cols))},
               "n": n,
               **q,
               "mean": float(sub[value_col].mean()),
               "std": float(sub[value_col].std()),
              }
        if weight_col and weight_col in sub.columns:
            row["wmean"] = weighted_mean(sub[value_col], sub[weight_col])
        rows.append(row)

    out = pd.DataFrame(rows)
    return out.sort_values("n", ascending=False)


def monthly_median(df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    if date_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame()
    d = df.dropna(subset=[date_col, value_col]).copy()
    if d.empty:
        return pd.DataFrame()
    dt = pd.to_datetime(d[date_col], errors="coerce")
    # remove tz to avoid warnings
    if hasattr(dt.dt, "tz") and dt.dt.tz is not None:
        dt = dt.dt.tz_convert(None)
    d["_month"] = dt.dt.to_period("M").dt.to_timestamp()
    d[value_col] = _num(d[value_col])
    out = d.groupby("_month")[value_col].median().reset_index()
    out.columns = ["month", "median"]
    return out.sort_values("month")


def coverage_table(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    n = len(df)
    for c in cols:
        if c not in df.columns:
            rows.append({"column": c, "coverage": 0.0, "non_null": 0, "total": n})
        else:
            nn = int(df[c].notna().sum())
            rows.append({"column": c, "coverage": float(nn / n) if n else 0.0, "non_null": nn, "total": n})
    return pd.DataFrame(rows).sort_values("coverage", ascending=True)
