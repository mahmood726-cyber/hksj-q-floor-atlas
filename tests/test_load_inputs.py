"""Tests for src.load_inputs — parquet load + SHA verify + D₁ filter."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import pytest

from src.load_inputs import (
    load_full_method_results,
    filter_to_d1,
    verify_input_sha,
    InputSHAMismatchError,
    InputMissingError,
)

PARQUET = Path("data/inputs/full_method_results.parquet")
SHA_FILE = Path("data/inputs/full_method_results.sha256")


class TestSHAVerify:
    def test_matching_sha_passes(self):
        verify_input_sha(PARQUET, SHA_FILE)

    def test_missing_parquet_raises(self, tmp_path):
        with pytest.raises(InputMissingError):
            verify_input_sha(tmp_path / "nope.parquet", SHA_FILE)

    def test_missing_sha_file_raises(self, tmp_path):
        with pytest.raises(InputMissingError):
            verify_input_sha(PARQUET, tmp_path / "nope.sha256")

    def test_sha_mismatch_raises(self, tmp_path):
        bad_sha = tmp_path / "bad.sha256"
        bad_sha.write_text("0" * 64 + "  full_method_results.parquet\n")
        with pytest.raises(InputSHAMismatchError) as exc:
            verify_input_sha(PARQUET, bad_sha)
        assert "expected" in str(exc.value).lower()


class TestLoadParquet:
    def test_loads_all_rows(self):
        df = load_full_method_results(PARQUET, SHA_FILE)
        assert len(df) == 19158

    def test_has_required_columns(self):
        df = load_full_method_results(PARQUET, SHA_FILE)
        for col in ["ma_id", "method", "estimate", "se", "ci_lo", "ci_hi",
                    "tau2", "i2", "k_effective", "converged", "reason_code"]:
            assert col in df.columns, f"missing column: {col}"

    def test_methods_present(self):
        df = load_full_method_results(PARQUET, SHA_FILE)
        assert set(df.method.unique()) == {"DL", "REML_only", "REML_HKSJ_PI"}


class TestFilterD1:
    @pytest.fixture(scope="class")
    def df(self):
        return load_full_method_results(PARQUET, SHA_FILE)

    def test_filters_to_reml_hksj_pi(self, df):
        d1 = filter_to_d1(df)
        assert set(d1.method.unique()) == {"REML_HKSJ_PI"}

    def test_filters_to_converged(self, df):
        d1 = filter_to_d1(df)
        assert d1.converged.all()

    def test_filters_to_i2_zero(self, df):
        d1 = filter_to_d1(df)
        assert (d1.i2 == 0.0).all()

    def test_filters_k_at_least_2(self, df):
        d1 = filter_to_d1(df)
        assert (d1.k_effective >= 2).all()

    def test_d1_size_in_expected_range(self, df):
        d1 = filter_to_d1(df)
        # spec §1.3: D₁ ≈ 3,500 (3,500 ± 200 acceptance band)
        assert 3300 <= len(d1) <= 3700, f"D₁ size {len(d1)} outside expected band"

    def test_ma_id_unique_in_d1(self, df):
        d1 = filter_to_d1(df)
        assert d1.ma_id.is_unique
