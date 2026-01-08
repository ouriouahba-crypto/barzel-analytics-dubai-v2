import pandas as pd

def add_facts(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # price_per_sqm (core)
    if "price" in out.columns and "size_sqm" in out.columns:
        out["price_per_sqm"] = out["price"] / out["size_sqm"]
        # hard guardrails (keeps visuals readable)
        out.loc[(out["price_per_sqm"] < 1000) | (out["price_per_sqm"] > 25000), "price_per_sqm"] = None

    # days_active (liquidity proxy)
    if "first_seen" in out.columns:
        now = pd.Timestamp.utcnow()
        last = out["last_seen"] if "last_seen" in out.columns else pd.NaT
        out["days_active"] = (last.fillna(now) - out["first_seen"]).dt.days
        out.loc[(out["days_active"] < 0) | (out["days_active"] > 3650), "days_active"] = None

    return out
