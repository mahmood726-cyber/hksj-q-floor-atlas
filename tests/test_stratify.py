"""Tests for src.stratify — k-strata aggregation."""
from __future__ import annotations

import pandas as pd
import pytest

from src.stratify import K_STRATA, assign_k_stratum, stratify_atlas


def _df(rows):
    return pd.DataFrame(rows)


class TestAssignStratum:
    @pytest.mark.parametrize("k,expected", [
        (2, "k=2"), (3, "k=3"),
        (4, "k=4-5"), (5, "k=4-5"),
        (6, "k=6-9"), (9, "k=6-9"),
        (10, "k>=10"), (50, "k>=10"),
    ])
    def test_boundary_assignment(self, k, expected):
        assert assign_k_stratum(k) == expected

    def test_k_lt_2_raises(self):
        with pytest.raises(ValueError):
            assign_k_stratum(1)


class TestStratify:
    @pytest.fixture
    def impact_df(self):
        # 10 rows: 2 each in k=2, k=3, k=4-5, k=6-9, k>=10
        rows = []
        for k_val, n in [(2, 2), (3, 2), (4, 2), (7, 2), (12, 2)]:
            for i in range(n):
                rows.append({
                    "ma_id": f"M{k_val}_{i}",
                    "k": k_val,
                    "ci_width_ratio": 1.0 + 0.5 * (i + 1),  # 1.5, 2.0
                    "sig_loss": bool(i),
                })
        return _df(rows)

    def test_strata_present(self, impact_df):
        out = stratify_atlas(impact_df)
        assert set(out["stratum"]) == set(K_STRATA) | {"overall"}

    def test_n_per_stratum(self, impact_df):
        out = stratify_atlas(impact_df).set_index("stratum")
        for s in K_STRATA:
            assert out.loc[s, "n"] == 2
        assert out.loc["overall", "n"] == 10

    def test_median_ratio(self, impact_df):
        out = stratify_atlas(impact_df).set_index("stratum")
        # For each stratum with ratios [1.5, 2.0], median = 1.75
        for s in K_STRATA:
            assert abs(out.loc[s, "median_ci_width_ratio"] - 1.75) < 1e-9

    def test_iqr_columns_present(self, impact_df):
        out = stratify_atlas(impact_df)
        for col in ["q25_ci_width_ratio", "q75_ci_width_ratio",
                    "p95_ci_width_ratio"]:
            assert col in out.columns

    def test_pct_sig_loss(self, impact_df):
        # Each stratum has [False, True] -> 50%
        out = stratify_atlas(impact_df).set_index("stratum")
        for s in K_STRATA:
            assert abs(out.loc[s, "pct_sig_loss"] - 50.0) < 1e-9
        assert abs(out.loc["overall", "pct_sig_loss"] - 50.0) < 1e-9

    def test_strata_sum_to_overall(self, impact_df):
        out = stratify_atlas(impact_df).set_index("stratum")
        n_strata_sum = sum(out.loc[s, "n"] for s in K_STRATA)
        assert n_strata_sum == out.loc["overall", "n"]

    def test_empty_stratum_handled(self):
        # If a stratum has 0 MAs, row still emitted with n=0 and NaN metrics
        df = _df([{"ma_id": "X", "k": 2, "ci_width_ratio": 1.2, "sig_loss": False}])
        out = stratify_atlas(df).set_index("stratum")
        assert out.loc["k=2", "n"] == 1
        assert out.loc["k>=10", "n"] == 0
        assert pd.isna(out.loc["k>=10", "median_ci_width_ratio"])
