"""Parquet loader for cochrane-modern-re full_method_results + D₁ filter.

The input parquet is SHA-pinned. Any mismatch fails closed.
D₁ = REML_HKSJ_PI rows that are converged AND I²=0 AND k≥2.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


class InputMissingError(FileNotFoundError):
    """Raised when an expected input file is missing."""


class InputSHAMismatchError(ValueError):
    """Raised when the input parquet's SHA-256 does not match the pinned hash."""


def _read_pinned_sha(sha_file: Path) -> str:
    """Read the first 64 hex chars from a sha256sum-format file."""
    line = sha_file.read_text().strip().split()[0]
    if len(line) != 64:
        raise ValueError(f"malformed sha file (expected 64 hex chars): {sha_file}")
    return line.lower()


def verify_input_sha(parquet: Path, sha_file: Path) -> None:
    """Raise InputMissingError / InputSHAMismatchError on any failure."""
    if not parquet.exists():
        raise InputMissingError(f"input parquet missing: {parquet}")
    if not sha_file.exists():
        raise InputMissingError(f"sha file missing: {sha_file}")
    pinned = _read_pinned_sha(sha_file)
    actual = hashlib.sha256(parquet.read_bytes()).hexdigest()
    if actual != pinned:
        raise InputSHAMismatchError(
            f"input parquet SHA mismatch: expected {pinned}, got {actual}"
        )


def load_full_method_results(parquet: Path, sha_file: Path) -> pd.DataFrame:
    """Verify SHA, then load the parquet."""
    verify_input_sha(parquet, sha_file)
    return pd.read_parquet(parquet)


def filter_to_d1(df: pd.DataFrame) -> pd.DataFrame:
    """Apply spec §1.3 D₁ filter: REML_HKSJ_PI ∩ converged ∩ i2==0 ∩ k≥2."""
    mask = (
        (df["method"] == "REML_HKSJ_PI")
        & (df["converged"] == True)  # noqa: E712 (explicit for parquet bool)
        & (df["i2"] == 0.0)
        & (df["k_effective"] >= 2)
    )
    return df.loc[mask].reset_index(drop=True)
