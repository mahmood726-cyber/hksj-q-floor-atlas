"""k-strata aggregation per spec §1.4."""
from __future__ import annotations

import numpy as np
import pandas as pd


K_STRATA = ["k=2", "k=3", "k=4-5", "k=6-9", "k>=10"]


def assign_k_stratum(k: int) -> str:
    if k < 2:
        raise ValueError(f"k<2 not allowed (got {k})")
    if k == 2:
        return "k=2"
    if k == 3:
        return "k=3"
    if k in (4, 5):
        return "k=4-5"
    if 6 <= k <= 9:
        return "k=6-9"
    return "k>=10"


def _summary_for(group: pd.DataFrame) -> dict:
    if len(group) == 0:
        return {
            "n": 0,
            "median_ci_width_ratio": np.nan,
            "q25_ci_width_ratio": np.nan,
            "q75_ci_width_ratio": np.nan,
            "p95_ci_width_ratio": np.nan,
            "pct_sig_loss": np.nan,
        }
    return {
        "n": int(len(group)),
        "median_ci_width_ratio": float(group["ci_width_ratio"].median()),
        "q25_ci_width_ratio": float(group["ci_width_ratio"].quantile(0.25)),
        "q75_ci_width_ratio": float(group["ci_width_ratio"].quantile(0.75)),
        "p95_ci_width_ratio": float(group["ci_width_ratio"].quantile(0.95)),
        "pct_sig_loss": float(100.0 * group["sig_loss"].mean()),
    }


def stratify_atlas(impact: pd.DataFrame) -> pd.DataFrame:
    """Build atlas.csv-shaped output: 1 row per stratum + 1 overall row."""
    impact = impact.copy()
    impact["stratum"] = impact["k"].map(assign_k_stratum)

    rows = []
    for s in K_STRATA:
        group = impact[impact["stratum"] == s]
        rows.append({"stratum": s, **_summary_for(group)})
    rows.append({"stratum": "overall", **_summary_for(impact)})
    return pd.DataFrame(rows)
