import pandas as pd


def add_facts(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # --- datetime normalization ---
    for c in ["first_seen", "last_seen", "scraped_at"]:
        if c in out.columns:
            out[c] = pd.to_datetime(out[c], errors="coerce", utc=True)

    # --- canonical: price_per_sqm ---
    # Prefer already-computed columns if present
    if "weighted_price_per_sqm_aed" in out.columns:
        out["price_per_sqm"] = out["weighted_price_per_sqm_aed"]
    elif "price_per_sqm_aed" in out.columns:
        out["price_per_sqm"] = out["price_per_sqm_aed"]
    else:
        # fallback: compute from sale_price_aed (or price) / size_sqm
        price_col = None
        if "sale_price_aed" in out.columns:
            price_col = "sale_price_aed"
        elif "price" in out.columns:
            price_col = "price"

        if price_col and "size_sqm" in out.columns:
            out["price_per_sqm"] = out[price_col] / out["size_sqm"]
        else:
            out["price_per_sqm"] = None

    # Keep visuals readable (guardrails)
    if "price_per_sqm" in out.columns:
        out.loc[(out["price_per_sqm"] < 1000) | (out["price_per_sqm"] > 250000), "price_per_sqm"] = None

    # --- canonical: days_on_market ---
    if "days_on_market" in out.columns:
        out["days_on_market"] = pd.to_numeric(out["days_on_market"], errors="coerce")
    else:
        # fallback: compute from first_seen/last_seen
        if "first_seen" in out.columns:
            now = pd.Timestamp.utcnow()
            last = out["last_seen"] if "last_seen" in out.columns else pd.NaT
            out["days_on_market"] = (last.fillna(now) - out["first_seen"]).dt.days
        else:
            out["days_on_market"] = None

    if "days_on_market" in out.columns:
        out.loc[(out["days_on_market"] < 0) | (out["days_on_market"] > 3650), "days_on_market"] = None

    # --- canonical: yields ---
    # Prefer already computed (your CSV already has these)
    if "net_yield_adj_vacancy_pct" in out.columns:
        out["net_yield"] = pd.to_numeric(out["net_yield_adj_vacancy_pct"], errors="coerce")
    elif "net_yield_est_pct" in out.columns:
        out["net_yield"] = pd.to_numeric(out["net_yield_est_pct"], errors="coerce")
    else:
        out["net_yield"] = None

    if "gross_yield_pct" in out.columns:
        out["gross_yield"] = pd.to_numeric(out["gross_yield_pct"], errors="coerce")
    else:
        out["gross_yield"] = None

    # --- canonical: service charge per sqm per year ---
    if "service_charge_aed_per_sqm_year" in out.columns:
        out["service_charge_psm_year"] = pd.to_numeric(out["service_charge_aed_per_sqm_year"], errors="coerce")
    else:
        out["service_charge_psm_year"] = None

    # --- vacancy ---
    if "vacancy_days_est" in out.columns:
        out["vacancy_days"] = pd.to_numeric(out["vacancy_days_est"], errors="coerce")
    else:
        out["vacancy_days"] = None

    # --- terrace ---
    if "has_terrace" in out.columns:
        # normalize to bool-ish
        out["has_terrace"] = out["has_terrace"].astype(str).str.lower().isin(["1", "true", "yes"])
    else:
        out["has_terrace"] = None

    if "terrace_size_sqm" in out.columns:
        out["terrace_size_sqm"] = pd.to_numeric(out["terrace_size_sqm"], errors="coerce")
    else:
        out["terrace_size_sqm"] = None

    return out
