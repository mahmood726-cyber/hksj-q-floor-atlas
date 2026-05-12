"""Tests for src.unfloored_engine — R subprocess wrapper."""
from __future__ import annotations

import pytest

from src.unfloored_engine import (
    UnfloorRequest,
    UnfloorResult,
    run_unfloored_hksj,
    REngineError,
)


SYNTHETIC_MA = UnfloorRequest(
    ma_id="SYNTH_001",
    yi=[0.20, 0.18],
    vi=[0.04, 0.04],
)


class TestRequest:
    def test_request_round_trip(self):
        r = UnfloorRequest(ma_id="X", yi=[0.1, 0.2], vi=[0.01, 0.01])
        assert r.ma_id == "X"
        assert r.k == 2

    def test_request_validates_length_match(self):
        with pytest.raises(ValueError):
            UnfloorRequest(ma_id="X", yi=[0.1, 0.2], vi=[0.01])

    def test_request_rejects_k_lt_2(self):
        with pytest.raises(ValueError):
            UnfloorRequest(ma_id="X", yi=[0.1], vi=[0.01])

    def test_request_rejects_nonpositive_variance(self):
        with pytest.raises(ValueError):
            UnfloorRequest(ma_id="X", yi=[0.1, 0.2], vi=[0.0, 0.01])


class TestEngine:
    def test_returns_unfloor_result_on_synthetic(self):
        res = run_unfloored_hksj(SYNTHETIC_MA)
        assert isinstance(res, UnfloorResult)
        assert res.ma_id == "SYNTH_001"
        assert res.converged is True
        assert res.k == 2

    def test_se_is_finite_positive(self):
        res = run_unfloored_hksj(SYNTHETIC_MA)
        assert res.se > 0
        assert res.se < 10

    def test_ci_lo_lt_ci_hi(self):
        res = run_unfloored_hksj(SYNTHETIC_MA)
        assert res.ci_lo < res.ci_hi

    def test_estimate_between_ci_bounds(self):
        res = run_unfloored_hksj(SYNTHETIC_MA)
        assert res.ci_lo <= res.estimate <= res.ci_hi


class TestBatch:
    def test_batch_runs_multiple_mas(self):
        from src.unfloored_engine import run_unfloored_batch
        results = run_unfloored_batch([
            UnfloorRequest(ma_id="A", yi=[0.1, 0.2], vi=[0.01, 0.01]),
            UnfloorRequest(ma_id="B", yi=[0.3, 0.4], vi=[0.02, 0.02]),
        ])
        assert len(results) == 2
        assert {r.ma_id for r in results} == {"A", "B"}


class TestGoldens:
    """Engine output must match independent metafor reference within 1e-6."""

    @pytest.mark.parametrize("idx", [0, 1, 2])
    def test_golden_matches_reference(self, golden_mas, idx):
        g = golden_mas[idx]
        if g["unfloored_expected"] is None:
            pytest.fail(f"golden_mas[{idx}].unfloored_expected not filled in")
        req = UnfloorRequest(ma_id=g["ma_id"], yi=g["yi"], vi=g["vi"])
        res = run_unfloored_hksj(req)
        exp = g["unfloored_expected"]
        for field in ["estimate", "se", "ci_lo", "ci_hi"]:
            assert abs(getattr(res, field) - exp[field]) < 1e-6, (
                f"{g['ma_id']}: {field} engine={getattr(res, field):.10f} "
                f"ref={exp[field]:.10f}"
            )
