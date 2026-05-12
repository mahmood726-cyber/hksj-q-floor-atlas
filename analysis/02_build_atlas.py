"""Join floored <-> unfloored, derive impact metrics, stratify, write atlas.

Handles Q=0 split per AMENDMENTS.md#amendment-1:
- D1a (Q>0) -> primary ratio + sig_loss summary
- D1b (Q=0) -> separate row with n + pct_sig_loss
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.diff_engine import join_floored_unfloored  # noqa: E402
from src.load_inputs import filter_to_d1, load_full_method_results  # noqa: E402
from src.stratify import stratify_atlas  # noqa: E402

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

PARQUET = ROOT / "data" / "inputs" / "full_method_results.parquet"
SHA = ROOT / "data" / "inputs" / "full_method_results.sha256"
UNFLOORED = ROOT / "outputs" / "unfloored.parquet"
PER_MA = ROOT / "outputs" / "per_ma_results.parquet"
ATLAS = ROOT / "outputs" / "atlas.csv"


def main():
    df = load_full_method_results(PARQUET, SHA)
    floored = filter_to_d1(df)
    log.info("floored D1 (total): %d", len(floored))

    if not UNFLOORED.exists():
        raise SystemExit(f"FATAL: run analysis/01_compute_unfloored.py first")

    unfloored = pd.read_parquet(UNFLOORED)
    log.info("unfloored: %d", len(unfloored))

    impact = join_floored_unfloored(floored, unfloored)
    log.info("impact rows: %d", len(impact))

    # Q=0 split (AMENDMENTS.md#amendment-1)
    q_zero_mask = impact["is_q_zero"]
    n_q_zero = int(q_zero_mask.sum())
    n_d1a = int((~q_zero_mask).sum())
    log.info("D1a (Q>0): %d   D1b (Q=0): %d", n_d1a, n_q_zero)

    # Property re-check on D1a (Q>0 only, where ratio is finite)
    d1a = impact[~q_zero_mask].copy()
    bad = d1a[d1a["ci_width_ratio"] < 1.0 - 1e-9]
    if not bad.empty:
        log.error("PROPERTY VIOLATION on D1a: %d rows with ratio < 1.0", len(bad))
        raise SystemExit(1)

    PER_MA.parent.mkdir(parents=True, exist_ok=True)
    impact.to_parquet(PER_MA, index=False)
    log.info("wrote %s (%d rows; D1a + D1b)", PER_MA, len(impact))

    # Primary atlas from D1a only
    atlas = stratify_atlas(d1a)

    # Append Q=0 summary row
    q_zero_rows = impact[q_zero_mask]
    q_zero_sig_loss_pct = (100.0 * q_zero_rows["sig_loss"].mean()
                           if len(q_zero_rows) > 0 else float("nan"))
    q_zero_row = {
        "stratum": "Q=0 (D1b)",
        "n": n_q_zero,
        "median_ci_width_ratio": float("inf"),
        "q25_ci_width_ratio": float("inf"),
        "q75_ci_width_ratio": float("inf"),
        "p95_ci_width_ratio": float("inf"),
        "pct_sig_loss": q_zero_sig_loss_pct,
    }
    atlas = pd.concat([atlas, pd.DataFrame([q_zero_row])], ignore_index=True)
    atlas.to_csv(ATLAS, index=False)
    log.info("wrote %s", ATLAS)

    # Print headline for human review
    overall = atlas[atlas["stratum"] == "overall"].iloc[0]
    print("\n=== HEADLINE (D1a, Q>0) ===")
    print(f"  n = {int(overall['n'])}")
    print(f"  median CI-width ratio:  {overall['median_ci_width_ratio']:.3f}x")
    print(f"  IQR:                    {overall['q25_ci_width_ratio']:.3f}-{overall['q75_ci_width_ratio']:.3f}x")
    print(f"  95th percentile:        {overall['p95_ci_width_ratio']:.3f}x")
    print(f"  significance lost:      {overall['pct_sig_loss']:.2f}%")
    print(f"\n=== Q=0 subset (D1b) ===")
    print(f"  n = {n_q_zero} ({100.0 * n_q_zero / len(impact):.2f}% of D1)")
    print(f"  sig_loss rate: {q_zero_sig_loss_pct:.2f}%")
    print(f"  ratio: unbounded (unfloored SE = 0 exactly)")


if __name__ == "__main__":
    main()
