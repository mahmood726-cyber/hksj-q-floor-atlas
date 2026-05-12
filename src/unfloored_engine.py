"""Python wrapper around hksj_unfloored.R via subprocess.

Batched: send N MAs in a single Rscript invocation to amortize R startup.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


R_EXE_CANDIDATES = [
    r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe",
    "Rscript",
]
R_SCRIPT = Path(__file__).parent / "r_scripts" / "hksj_unfloored.R"


class REngineError(RuntimeError):
    """R subprocess failed or returned an unparseable response."""


@dataclass(frozen=True)
class UnfloorRequest:
    ma_id: str
    yi: list[float]
    vi: list[float]

    def __post_init__(self):
        if len(self.yi) != len(self.vi):
            raise ValueError(
                f"yi/vi length mismatch for {self.ma_id}: "
                f"{len(self.yi)} vs {len(self.vi)}"
            )
        if len(self.yi) < 2:
            raise ValueError(f"k<2 not allowed (got k={len(self.yi)}) for {self.ma_id}")
        if any(v <= 0 for v in self.vi):
            raise ValueError(f"non-positive variance in {self.ma_id}: {self.vi}")

    @property
    def k(self) -> int:
        return len(self.yi)


@dataclass(frozen=True)
class UnfloorResult:
    ma_id: str
    estimate: float
    se: float
    ci_lo: float
    ci_hi: float
    tau2: float
    i2: float
    k: int
    converged: bool
    reason_code: str = ""


def _resolve_rscript() -> str:
    for candidate in R_EXE_CANDIDATES:
        if "\\" in candidate or "/" in candidate:
            if Path(candidate).exists():
                return candidate
        else:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
    raise REngineError(
        f"Rscript not found; tried: {R_EXE_CANDIDATES}. "
        "Install R 4.5.x or set PATH."
    )


def run_unfloored_batch(requests: Iterable[UnfloorRequest]) -> list[UnfloorResult]:
    requests = list(requests)
    payload = {
        "requests": [
            {"ma_id": r.ma_id, "yi": list(r.yi), "vi": list(r.vi)}
            for r in requests
        ]
    }
    rscript = _resolve_rscript()
    proc = subprocess.run(
        [rscript, str(R_SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise REngineError(f"Rscript failed (rc={proc.returncode}): {proc.stderr[:500]}")
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise REngineError(f"Rscript stdout not valid JSON: {e}\n{proc.stdout[:500]}")

    results: list[UnfloorResult] = []
    for row in parsed["results"]:
        if not row["converged"]:
            raise REngineError(
                f"R engine non-convergence for {row['ma_id']}: "
                f"reason_code={row['reason_code']}"
            )
        results.append(UnfloorResult(**row))
    return results


def run_unfloored_hksj(request: UnfloorRequest) -> UnfloorResult:
    """Single-MA convenience wrapper."""
    return run_unfloored_batch([request])[0]
