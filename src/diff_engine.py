"""Pairwise impact computation: floored vs unfloored CIs.

Property invariants enforced (spec §1.5(12)–(13)):
  - ci_width_ratio >= 1.0 - 1e-9 in I²=0 regime
  - sig_gain (unfloored not sig → floored sig) is impossible

Q=0 degeneracy (AMENDMENTS.md#amendment-1):
  When Q=0 exactly, unfloored HKSJ multiplier sqrt(Q/(k-1))=0, so
  ci_width_unfloored=0 and the ratio is undefined. We flag is_q_zero=True
  and set ci_width_ratio=math.inf for these rows.
"""
from __future__ import annotations

import math

import pandas as pd


_NULL_POINT = 0.0  # Pairwise70 / cochrane-modern-re convention (log scale, SMD, MD)
_RATIO_TOL = 1e-9


class PropertyViolationError(AssertionError):
    """Raised when an I²=0-regime invariant is violated. Indicates a bug."""


def _ci_excludes_null(ci_lo: float, ci_hi: float) -> bool:
    return ci_lo > _NULL_POINT or ci_hi < _NULL_POINT


def compute_impact_row(unfloored: dict, floored: dict) -> dict:
    """Per-MA: derive ci_width_ratio + sig_loss; enforce I²=0 invariants."""
    if unfloored["ma_id"] != floored["ma_id"]:
        raise ValueError(
            f"ma_id mismatch: unfloored={unfloored['ma_id']!r} "
            f"floored={floored['ma_id']!r}"
        )

    w_unfl = unfloored["ci_hi"] - unfloored["ci_lo"]
    w_floor = floored["ci_hi"] - floored["ci_lo"]

    if w_unfl == 0.0:
        # Q=0 degeneracy: unfloored HKSJ multiplier sqrt(Q/(k-1)) is exactly 0,
        # so SE_unfloored=0 and ci_width=0. The floor effect is unbounded.
        # Treat ratio as inf; sig_unfl is defined by the point estimate's
        # relation to the null (a zero-width CI at the estimate only EXCLUDES
        # the null when estimate != null).
        ratio = math.inf
        is_q_zero = True
    else:
        ratio = w_floor / w_unfl
        is_q_zero = False
        if ratio < 1.0 - _RATIO_TOL:
            raise PropertyViolationError(
                f"{unfloored['ma_id']}: ci_width_ratio={ratio:.10f} < 1.0 "
                f"(unfloored width={w_unfl:.6f}, floored width={w_floor:.6f}). "
                "Floor must widen the CI in I²=0; this is mathematically impossible."
            )

    sig_unfl = _ci_excludes_null(unfloored["ci_lo"], unfloored["ci_hi"])
    sig_floor = _ci_excludes_null(floored["ci_lo"], floored["ci_hi"])

    if (not sig_unfl) and sig_floor:
        raise PropertyViolationError(
            f"{unfloored['ma_id']}: sig_gain detected (unfloored not significant, "
            "floored significant). Mathematically impossible in I²=0 regime."
        )

    sig_loss = sig_unfl and (not sig_floor)

    return {
        "ma_id": unfloored["ma_id"],
        "k": unfloored.get("k", floored.get("k_effective")),
        "estimate": floored["estimate"],
        "se_unfloored": unfloored["se"],
        "se_floored": floored["se"],
        "ci_lo_unfloored": unfloored["ci_lo"],
        "ci_hi_unfloored": unfloored["ci_hi"],
        "ci_lo_floored": floored["ci_lo"],
        "ci_hi_floored": floored["ci_hi"],
        "ci_width_unfloored": w_unfl,
        "ci_width_floored": w_floor,
        "ci_width_ratio": ratio,
        "is_q_zero": is_q_zero,
        "sig_unfloored": sig_unfl,
        "sig_floored": sig_floor,
        "sig_loss": sig_loss,
    }


def join_floored_unfloored(
    floored: pd.DataFrame, unfloored: pd.DataFrame
) -> pd.DataFrame:
    """Inner-join on ma_id, derive impact metrics per row, return DataFrame."""
    if floored.empty:
        raise ValueError("floored frame is empty")

    missing = set(floored["ma_id"]) - set(unfloored["ma_id"] if not unfloored.empty else [])
    if missing:
        raise ValueError(
            f"missing unfloored values for {len(missing)} ma_id(s): "
            f"{sorted(list(missing))[:5]}..."
        )

    fl_idx = floored.set_index("ma_id")
    un_idx = unfloored.set_index("ma_id")

    rows: list[dict] = []
    for ma_id, un_row in un_idx.iterrows():
        fl_row = fl_idx.loc[ma_id]
        unfloored_dict = {"ma_id": ma_id, **un_row.to_dict()}
        floored_dict = {"ma_id": ma_id, **fl_row.to_dict()}
        rows.append(compute_impact_row(unfloored_dict, floored_dict))
    return pd.DataFrame(rows)
