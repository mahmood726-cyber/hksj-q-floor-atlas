"""Preflight: verify every external prereq before any compute runs.

Exit 0 if all good. Exit 1 with a clear FAIL log otherwise. Never silently skip.

Handles the path-fallback chain documented in PREFLIGHT.md: env var PAIRWISE70_DIR
OR cochrane-modern-re's paths_local.py DEFAULT_PAIRWISE70.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
_cmre_default = os.environ.get("COCHRANE_MODERN_RE_DIR", "")
COCHRANE_PARQUET = (
    Path(_cmre_default) / "outputs" / "full_method_results.parquet"
    if _cmre_default
    else Path("outputs") / "full_method_results.parquet"  # will fail exists() check below
)
LOCAL_PARQUET = ROOT / "data" / "inputs" / "full_method_results.parquet"
LOCAL_SHA = ROOT / "data" / "inputs" / "full_method_results.sha256"


def _resolve_pairwise70_dir() -> tuple[Path | None, str]:
    """Return (resolved_path, source_description)."""
    env = os.environ.get("PAIRWISE70_DIR")
    if env and Path(env).exists():
        return Path(env), f"env var PAIRWISE70_DIR={env}"
    try:
        cmre = os.environ.get("COCHRANE_MODERN_RE_DIR", "")
        if cmre:
            sys.path.insert(0, cmre)
        from src.paths_local import DEFAULT_PAIRWISE70  # type: ignore[import-untyped]
        if DEFAULT_PAIRWISE70 and DEFAULT_PAIRWISE70.exists():
            return DEFAULT_PAIRWISE70, f"paths_local.py DEFAULT_PAIRWISE70={DEFAULT_PAIRWISE70}"
    except Exception as e:
        return None, f"paths_local.py import failed: {e}"
    return None, "no env var and no paths_local fallback"


def main() -> int:
    fails: list[str] = []

    if not COCHRANE_PARQUET.exists():
        fails.append(f"cochrane-modern-re parquet missing: {COCHRANE_PARQUET}")

    if not LOCAL_PARQUET.exists():
        fails.append(f"local input copy missing (Task 2 not done): {LOCAL_PARQUET}")

    if not LOCAL_SHA.exists():
        fails.append(f"sha pin missing (Task 2 not done): {LOCAL_SHA}")

    if LOCAL_PARQUET.exists() and LOCAL_SHA.exists():
        sys.path.insert(0, str(ROOT))
        from src.load_inputs import InputSHAMismatchError, verify_input_sha
        try:
            verify_input_sha(LOCAL_PARQUET, LOCAL_SHA)
        except InputSHAMismatchError as e:
            fails.append(f"sha mismatch: {e}")

    pw_dir, source = _resolve_pairwise70_dir()
    if pw_dir is None:
        fails.append(f"PAIRWISE70_DIR not resolvable: {source}")
    else:
        print(f"PAIRWISE70 corpus: {pw_dir} (source: {source})")

    try:
        from src.loaders import iter_mas_with_log  # noqa: F401
        print("cochrane-modern-re loaders: importable")
    except Exception as e:
        fails.append(f"cochrane-modern-re loaders unimportable: {e}")

    r_exe = (r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe"
             if Path(r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe").exists()
             else shutil.which("Rscript"))
    if not r_exe:
        fails.append("Rscript not found")
    else:
        rc = subprocess.run(
            [r_exe, "-e", 'cat(as.character(packageVersion("metafor")))'],
            capture_output=True, text=True,
        )
        if rc.returncode != 0 or not rc.stdout.strip():
            fails.append(f"metafor unavailable: {rc.stderr[:200]}")
        else:
            print(f"R metafor: {rc.stdout.strip()}")

    ots = shutil.which("ots")
    if ots:
        print(f"OTS CLI: {ots} (note: lessons.md warns Python 3.13 may break SSL; web fallback available)")
    else:
        print("OTS CLI: absent; will use opentimestamps.org web stamper at Task 20")

    if fails:
        print("\nPREFLIGHT FAILED:")
        for f in fails:
            print(f"  FAIL: {f}")
        return 1
    print("\nPREFLIGHT OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
