"""Select 3 golden MAs deterministically: smallest k_effective, ma_id tiebreaker.

Writes tests/fixtures/golden_mas.json with the floored values (from cochrane-modern-re)
and study-level yi/vi (from the Pairwise70 loader). unfloored_expected is filled
later by scripts/fill_goldens.py via an independent metafor call.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Projects\cochrane-modern-re")
sys.path.insert(0, ".")

from src.load_inputs import filter_to_d1, load_full_method_results  # noqa: E402

PARQUET = Path("data/inputs/full_method_results.parquet")
SHA = Path("data/inputs/full_method_results.sha256")
OUT = Path("tests/fixtures/golden_mas.json")


def main():
    from src.loaders import iter_mas_with_log  # cochrane-modern-re loader

    df = load_full_method_results(PARQUET, SHA)
    d1 = filter_to_d1(df).sort_values(["k_effective", "ma_id"]).head(3)
    print("Chosen golden ma_ids:")
    for _, r in d1.iterrows():
        print(f"  {r.ma_id}  k={r.k_effective}  estimate={r.estimate:.6f}")

    result = iter_mas_with_log()
    by_id = {m.ma_id: m for m in result.mas}

    goldens = []
    for _, r in d1.iterrows():
        ma = by_id.get(r.ma_id)
        if ma is None:
            raise SystemExit(f"FATAL: ma_id {r.ma_id} not in Pairwise70 loader")
        # ma.studies is a tuple[Study, ...] where Study has .yi and .vi attributes
        goldens.append({
            "ma_id": r.ma_id,
            "k": int(r.k_effective),
            "yi": [float(s.yi) for s in ma.studies],
            "vi": [float(s.vi) for s in ma.studies],
            "floored": {
                "estimate": float(r.estimate),
                "se": float(r.se),
                "ci_lo": float(r.ci_lo),
                "ci_hi": float(r.ci_hi),
            },
            "unfloored_expected": None,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(goldens, indent=2))
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
