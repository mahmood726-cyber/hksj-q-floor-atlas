"""Tests for src.diff_engine — pairwise impact metric computation."""
from __future__ import annotations

import math

import pandas as pd
import pytest

from src.diff_engine import (
    compute_impact_row,
    join_floored_unfloored,
    PropertyViolationError,
)


def _row(estimate, se, ci_lo, ci_hi, ma_id="X", k=3):
    return {
        "ma_id": ma_id, "estimate": estimate, "se": se,
        "ci_lo": ci_lo, "ci_hi": ci_hi, "k": k,
    }


class TestComputeImpactRow:
    def test_ci_width_ratio_simple(self):
        unfloored = _row(0.1, 0.05, -0.005, 0.205)  # width 0.21
        floored   = _row(0.1, 0.08, -0.046, 0.246)  # width 0.292
        out = compute_impact_row(unfloored, floored)
        assert math.isclose(out["ci_width_ratio"], 0.292 / 0.21, rel_tol=1e-9)

    def test_sig_loss_true_when_loses_significance(self):
        unfloored = _row(0.3, 0.1, 0.05, 0.55)   # excludes 0
        floored   = _row(0.3, 0.2, -0.10, 0.70)  # includes 0
        out = compute_impact_row(unfloored, floored)
        assert out["sig_unfloored"] is True
        assert out["sig_floored"] is False
        assert out["sig_loss"] is True

    def test_sig_loss_false_when_both_significant(self):
        unfloored = _row(0.5, 0.1, 0.30, 0.70)
        floored   = _row(0.5, 0.12, 0.26, 0.74)
        out = compute_impact_row(unfloored, floored)
        assert out["sig_loss"] is False

    def test_sig_loss_false_when_neither_significant(self):
        unfloored = _row(0.1, 0.2, -0.30, 0.50)
        floored   = _row(0.1, 0.3, -0.49, 0.69)
        out = compute_impact_row(unfloored, floored)
        assert out["sig_loss"] is False

    def test_ci_width_ratio_less_than_one_raises(self):
        # Floored MUST be wider in I²=0 regime; less-than-one is a bug.
        unfloored = _row(0.1, 0.1, -0.10, 0.30)  # width 0.40
        floored   = _row(0.1, 0.05, 0.00, 0.20)  # width 0.20  -- impossible!
        with pytest.raises(PropertyViolationError):
            compute_impact_row(unfloored, floored)

    def test_sig_gain_raises(self):
        # Unfloored not significant, floored significant -- impossible in I²=0
        unfloored = _row(0.5, 0.5, -0.50, 1.50)
        floored   = _row(0.5, 0.1, 0.30, 0.70)
        with pytest.raises(PropertyViolationError):
            compute_impact_row(unfloored, floored)

    def test_ma_id_mismatch_raises(self):
        with pytest.raises(ValueError):
            compute_impact_row(_row(0.1, 0.1, 0, 0.2, ma_id="A"),
                               _row(0.1, 0.1, 0, 0.2, ma_id="B"))

    def test_carries_k_through(self):
        out = compute_impact_row(_row(0.1, 0.05, -0.005, 0.205, k=7),
                                 _row(0.1, 0.08, -0.046, 0.246, k=7))
        assert out["k"] == 7

    def test_ratio_at_floor_boundary(self):
        # When unfloored == floored (ratio == 1.0), no violation, no sig change
        unfloored = _row(0.1, 0.10, -0.096, 0.296)
        floored   = _row(0.1, 0.10, -0.096, 0.296)
        out = compute_impact_row(unfloored, floored)
        assert math.isclose(out["ci_width_ratio"], 1.0, abs_tol=1e-9)
        assert out["sig_loss"] is False


class TestJoinFlooredUnfloored:
    def test_inner_join_on_ma_id(self):
        floored = pd.DataFrame([
            {"ma_id": "A", "estimate": 0.1, "se": 0.08, "ci_lo": -0.046,
             "ci_hi": 0.246, "k_effective": 3},
            {"ma_id": "B", "estimate": 0.2, "se": 0.10, "ci_lo": 0.01,
             "ci_hi": 0.39, "k_effective": 4},
        ])
        unfloored = pd.DataFrame([
            {"ma_id": "A", "estimate": 0.1, "se": 0.05, "ci_lo": -0.005,
             "ci_hi": 0.205, "k": 3, "converged": True},
            {"ma_id": "B", "estimate": 0.2, "se": 0.07, "ci_lo": 0.08,
             "ci_hi": 0.32, "k": 4, "converged": True},
        ])
        out = join_floored_unfloored(floored, unfloored)
        assert len(out) == 2
        assert "ci_width_ratio" in out.columns
        assert "sig_loss" in out.columns
        assert (out["ci_width_ratio"] >= 1.0).all()

    def test_missing_unfloored_for_an_ma_raises(self):
        floored = pd.DataFrame([{"ma_id": "A", "estimate": 0.1, "se": 0.08,
                                  "ci_lo": -0.046, "ci_hi": 0.246, "k_effective": 3}])
        unfloored = pd.DataFrame([])  # empty
        with pytest.raises(ValueError, match="missing"):
            join_floored_unfloored(floored, unfloored)
