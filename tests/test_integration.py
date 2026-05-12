"""End-to-end integration test on a 10-MA subset of D1.

Exercises every module: load_inputs -> unfloored_engine -> diff_engine -> stratify.
Uses real Pairwise70 data (max_reviews=7 covers all 10 D1 head MAs in ~10s).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, r"C:\Projects\cochrane-modern-re")

from src.diff_engine import join_floored_unfloored
from src.load_inputs import filter_to_d1, load_full_method_results
from src.stratify import stratify_atlas
from src.unfloored_engine import UnfloorRequest, run_unfloored_batch


PARQUET = Path("data/inputs/full_method_results.parquet")
SHA = Path("data/inputs/full_method_results.sha256")

# max_reviews=7 covers CD000028/214/219/247/402/478 which hold all 10 D1 head MAs.
_MAX_REVIEWS_FOR_SUBSET = 7


@pytest.fixture(scope="module")
def small_d1():
    df = load_full_method_results(PARQUET, SHA)
    return filter_to_d1(df).head(10)


@pytest.fixture(scope="module")
def study_level_for(small_d1):
    """Dict {ma_id -> (yi_list, vi_list)} for the 10 subset MAs."""
    from src.loaders import iter_mas_with_log

    needed_ids = set(small_d1["ma_id"])
    result = iter_mas_with_log(max_reviews=_MAX_REVIEWS_FOR_SUBSET)
    by_id = {m.ma_id: m for m in result.mas}

    missing = needed_ids - set(by_id)
    if missing:
        pytest.skip(
            f"Pairwise70 corpus (max_reviews={_MAX_REVIEWS_FOR_SUBSET}) does not "
            f"contain {len(missing)} required MA(s): {sorted(missing)}. "
            "Increase _MAX_REVIEWS_FOR_SUBSET or check corpus path."
        )

    return {
        mid: (
            [float(s.yi) for s in by_id[mid].studies],
            [float(s.vi) for s in by_id[mid].studies],
        )
        for mid in needed_ids
    }


class TestPipeline:
    def test_full_pipeline_runs(self, small_d1, study_level_for):
        # ------------------------------------------------------------------ #
        # 1. Build UnfloorRequests and run the R engine on 10 MAs             #
        # ------------------------------------------------------------------ #
        reqs = [
            UnfloorRequest(ma_id=mid, yi=yv[0], vi=yv[1])
            for mid, yv in study_level_for.items()
        ]
        unfloored_results = run_unfloored_batch(reqs)
        assert len(unfloored_results) == 10, (
            f"Expected 10 unfloored results, got {len(unfloored_results)}"
        )

        # ------------------------------------------------------------------ #
        # 2. Build unfloored DataFrame                                         #
        # ------------------------------------------------------------------ #
        unfloored_df = pd.DataFrame([
            {
                "ma_id": r.ma_id,
                "estimate": r.estimate,
                "se": r.se,
                "ci_lo": r.ci_lo,
                "ci_hi": r.ci_hi,
                "k": r.k,
                "converged": r.converged,
            }
            for r in unfloored_results
        ])

        # ------------------------------------------------------------------ #
        # 3. Join floored (D1 parquet) with unfloored                         #
        # ------------------------------------------------------------------ #
        impact = join_floored_unfloored(small_d1, unfloored_df)
        assert len(impact) == 10, f"Expected 10 impact rows, got {len(impact)}"

        # Floor must widen or preserve CI (invariant from spec §1.5(12))
        violations = impact[impact["ci_width_ratio"] < 1.0 - 1e-9]
        assert len(violations) == 0, (
            f"ci_width_ratio < 1.0 for {len(violations)} MAs: "
            f"{violations[['ma_id', 'ci_width_ratio']].to_dict('records')}"
        )

        # ------------------------------------------------------------------ #
        # 4. No significance gain: unfloored not sig -> floored sig            #
        # ------------------------------------------------------------------ #
        sig_gain = (~impact["sig_unfloored"]) & impact["sig_floored"]
        assert not sig_gain.any(), (
            f"Impossible sig_gain detected for {sig_gain.sum()} MA(s) "
            f"(mathematically impossible in I²=0 regime)"
        )

        # ------------------------------------------------------------------ #
        # 5. Stratify and check overall row                                    #
        # ------------------------------------------------------------------ #
        atlas = stratify_atlas(impact)
        assert "overall" in atlas["stratum"].values, "stratify_atlas missing 'overall' row"

        overall = atlas[atlas["stratum"] == "overall"].iloc[0]
        assert overall["n"] == 10, f"overall n={overall['n']}, expected 10"
        assert overall["median_ci_width_ratio"] >= 1.0, (
            f"median_ci_width_ratio={overall['median_ci_width_ratio']:.6f} < 1.0 "
            "(floor must never narrow CI)"
        )

        # Print the actual value so the caller can record it for sanity check
        print(
            f"\n[integration] overall median_ci_width_ratio = "
            f"{overall['median_ci_width_ratio']:.6f}"
        )
        print(
            f"[integration] ci_width_ratio range: "
            f"[{impact['ci_width_ratio'].min():.6f}, {impact['ci_width_ratio'].max():.6f}]"
        )

        # Soft assertion: at least one MA shows measurable inflation (> 1.001)
        # This is expected on real Cochrane data where Q/(k-1) often deviates from 1.
        # If all 10 happen to have Q/(k-1) ~ 1, this will fire; relax to >= 1.0
        # per the task spec "possible deviation" clause.
        any_inflated = (impact["ci_width_ratio"] > 1.001).any()
        if not any_inflated:
            pytest.xfail(
                "All 10 D1 head MAs have ci_width_ratio extremely close to 1.0 "
                "(Q/(k-1) near 1 for every MA in this subset). "
                "The floor still holds (ratio >= 1.0). "
                "Widen the subset or use a different slice to find more inflated MAs."
            )
