import pandas as pd

from src.analytics.kpi_engine import (
    kpi_pricing,
    kpi_liquidity,
    kpi_yield,
    kpi_costs,
    kpi_terrace,
)

from src.analytics.advanced_kpis import (
    price_consistency_index,
    liquidity_depth_ratio,
    yield_efficiency_ratio,
    vacancy_drag_index,
    cost_to_yield_ratio,
)


def snapshot(df: pd.DataFrame) -> dict:
    base = {
        "n_obs": int(len(df)),
        **kpi_pricing(df),
        **kpi_liquidity(df),
        **kpi_yield(df),
        **kpi_costs(df),
        **kpi_terrace(df),
    }

    # Advanced (still factual)
    base.update(
        {
            "price_consistency_cv": price_consistency_index(df),
            "liquidity_depth_ratio": liquidity_depth_ratio(df),
            "yield_efficiency_ratio": yield_efficiency_ratio(df),
            "vacancy_drag_index": vacancy_drag_index(df),
            "cost_to_yield_ratio": cost_to_yield_ratio(df),
        }
    )

    return base


def snapshots_by(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if group_col not in df.columns:
        return pd.DataFrame()
    rows = []
    for key, sub in df.groupby(group_col, dropna=True):
        row = snapshot(sub)
        row[group_col] = key
        rows.append(row)
    return pd.DataFrame(rows)
