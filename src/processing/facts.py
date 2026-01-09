import pandas as pd


def add_facts(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # --- datetime normalization ---
    for c in ["first_seen", "last_seen", "scraped_at"]:
        if c in out.columns:
            out[c] = pd.to_datetime(out[c], errors="coerce", utc=True)

    # Ensure numeric base columns if present
    for c in [
        "weighted_price_per_sqm_aed",
        "price_per_sqm_aed",
        "sale_price_aed",
        "price",
        "size_sqm",
        "service_charge_aed_per_sqm_year",
        "gross_yield_pct",
        "net_yield_est_pct",
        "net_yield_adj_vacancy_pct",
        "days_on_market",
        "vacancy_days_est",
        "floor",
        "total_floors",
        "bedrooms",
        "bathrooms",
    ]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")

    # --- canonical: price_per_sqm ---
    # Prefer already-computed columns if present
    if "weighted_price_per_sqm_aed" in out.columns and out["weighted_price_per_sqm_aed"].notna().any():
        out["price_per_sqm"] = out["weighted_price_per_sqm_aed"]
    elif "price_per_sqm_aed" in out.columns and out["price_per_sqm_aed"].notna().any():
        out["price_per_sqm"] = out["price_per_sqm_aed"]
    else:
        # fallback: compute from sale_price_aed (or price) / size_sqm
        price_col = None
        if "sale_price_aed" in out.columns and out["sale_price_aed"].notna().any():
            price_col = "sale_price_aed"
        elif "price" in out.columns and out["price"].notna().any():
            price_col = "price"

        if price_col and "size_sqm" in out.columns:
            denom = out["size_sqm"].replace({0: pd.NA})
            out["price_per_sqm"] = out[price_col] / denom
        else:
            out["price_per_sqm"] = pd.NA

    # Guardrails (keep, but safer)
    # Dubai AED/sqm typically ~5k–150k depending on asset; set wide bounds to avoid nuking data.
    if "price_per_sqm" in out.columns:
        out.loc[(out["price_per_sqm"] < 2000) | (out["price_per_sqm"] > 400000), "price_per_sqm"] = pd.NA

    # --- canonical: days_on_market ---
    if "days_on_market" in out.columns and out["days_on_market"].notna().any():
        out["days_on_market"] = pd.to_numeric(out["days_on_market"], errors="coerce")
    else:
        # fallback: compute from first_seen/last_seen
        if "first_seen" in out.columns:
            now = pd.Timestamp.utcnow()
            last = out["last_seen"] if "last_seen" in out.columns else pd.NaT
            out["days_on_market"] = (last.fillna(now) - out["first_seen"]).dt.days
        else:
            out["days_on_market"] = pd.NA

    if "days_on_market" in out.columns:
        out.loc[(out["days_on_market"] < 0) | (out["days_on_market"] > 3650), "days_on_market"] = pd.NA

    # --- canonical: yields ---
    if "net_yield_adj_vacancy_pct" in out.columns and out["net_yield_adj_vacancy_pct"].notna().any():
        out["net_yield"] = out["net_yield_adj_vacancy_pct"]
    elif "net_yield_est_pct" in out.columns and out["net_yield_est_pct"].notna().any():
        out["net_yield"] = out["net_yield_est_pct"]
    else:
        out["net_yield"] = pd.NA

    if "gross_yield_pct" in out.columns and out["gross_yield_pct"].notna().any():
        out["gross_yield"] = out["gross_yield_pct"]
    else:
        out["gross_yield"] = pd.NA

    # Guardrails yields (optional but prevents crazy values)
    out.loc[(out["net_yield"] < -5) | (out["net_yield"] > 40), "net_yield"] = pd.NA
    out.loc[(out["gross_yield"] < -5) | (out["gross_yield"] > 40), "gross_yield"] = pd.NA

    # --- canonical: service charge per sqm per year ---
    if "service_charge_aed_per_sqm_year" in out.columns and out["service_charge_aed_per_sqm_year"].notna().any():
        out["service_charge_psm_year"] = out["service_charge_aed_per_sqm_year"]
    else:
        out["service_charge_psm_year"] = pd.NA

    # Guardrails charges
    out.loc[(out["service_charge_psm_year"] < 0) | (out["service_charge_psm_year"] > 100000), "service_charge_psm_year"] = pd.NA

    # --- vacancy ---
    if "vacancy_days_est" in out.columns and out["vacancy_days_est"].notna().any():
        out["vacancy_days"] = out["vacancy_days_est"]
    else:
        out["vacancy_days"] = pd.NA

    out.loc[(out["vacancy_days"] < 0) | (out["vacancy_days"] > 3650), "vacancy_days"] = pd.NA

    # --- terrace ---
    if "has_terrace" in out.columns:
        # normalize to bool-ish
        out["has_terrace"] = out["has_terrace"].astype(str).str.lower().isin(["1", "true", "yes"])
    else:
        out["has_terrace"] = pd.NA

    if "terrace_size_sqm" in out.columns:
        out["terrace_size_sqm"] = pd.to_numeric(out["terrace_size_sqm"], errors="coerce")
    else:
        out["terrace_size_sqm"] = pd.NA

    return out
