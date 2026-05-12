"""Merge reference values into tests/fixtures/golden_mas.json."""
from __future__ import annotations

import json
from pathlib import Path

GOLDENS = Path("tests/fixtures/golden_mas.json")
REF = Path("tests/fixtures/golden_mas_reference.json")


def main():
    goldens = json.loads(GOLDENS.read_text())
    reference = json.loads(REF.read_text())
    ref_by_id = {r["ma_id"]: r for r in reference}

    for item in goldens:
        ref = ref_by_id[item["ma_id"]]
        item["unfloored_expected"] = {
            "estimate": ref["estimate"],
            "se": ref["se"],
            "ci_lo": ref["ci_lo"],
            "ci_hi": ref["ci_hi"],
        }

    GOLDENS.write_text(json.dumps(goldens, indent=2))
    print(f"filled {len(goldens)} MAs in {GOLDENS}")


if __name__ == "__main__":
    main()
