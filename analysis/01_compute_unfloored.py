"""Run un-floored HKSJ on every D1 MA, write outputs/unfloored.parquet.

Resume-safe: if outputs/unfloored.parquet exists, skip already-computed ma_ids.
Batched: groups of 50 MAs per Rscript invocation.
"""
from __future__ import annotations

import logging
import os
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
_cmre_dir = os.environ.get("COCHRANE_MODERN_RE_DIR", "")
if _cmre_dir:
    sys.path.insert(0, _cmre_dir)

from src.load_inputs import filter_to_d1, load_full_method_results  # noqa: E402
from src.unfloored_engine import UnfloorRequest, run_unfloored_batch  # noqa: E402

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

PARQUET = ROOT / "data" / "inputs" / "full_method_results.parquet"
SHA = ROOT / "data" / "inputs" / "full_method_results.sha256"
OUT = ROOT / "outputs" / "unfloored.parquet"
BATCH = 50


def main(limit: int | None = None):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = load_full_method_results(PARQUET, SHA)
    d1 = filter_to_d1(df)
    if limit is not None:
        d1 = d1.head(limit)
    log.info("D1 size: %d", len(d1))

    already_done: set[str] = set()
    if OUT.exists():
        prev = pd.read_parquet(OUT)
        already_done = set(prev["ma_id"])
        log.info("resume: %d already computed", len(already_done))
    else:
        prev = pd.DataFrame()

    todo = d1[~d1["ma_id"].isin(already_done)].copy()
    log.info("todo: %d", len(todo))

    if len(todo) == 0:
        log.info("nothing to do; %d already in %s", len(prev), OUT)
        return

    from src.loaders import iter_mas_with_log
    pw = iter_mas_with_log()
    by_id = {m.ma_id: m for m in pw.mas}

    new_rows: list[dict] = []
    skipped: list[str] = []
    for start in range(0, len(todo), BATCH):
        batch = todo.iloc[start:start + BATCH]
        reqs: list[UnfloorRequest] = []
        for _, r in batch.iterrows():
            ma = by_id.get(r.ma_id)
            if ma is None:
                skipped.append(r.ma_id)
                continue
            reqs.append(UnfloorRequest(
                ma_id=r.ma_id,
                yi=[float(s.yi) for s in ma.studies],
                vi=[float(s.vi) for s in ma.studies],
            ))
        if not reqs:
            continue
        results = run_unfloored_batch(reqs)
        new_rows.extend(asdict(r) for r in results)
        log.info("batch %d-%d: %d done; cumulative %d/%d",
                 start, start + len(batch), len(results),
                 len(prev) + len(new_rows), len(d1))

        # Checkpoint every 5 batches
        if (start // BATCH) % 5 == 4:
            combined = pd.concat([prev, pd.DataFrame(new_rows)],
                                 ignore_index=True)
            combined.to_parquet(OUT, index=False)
            log.info("checkpoint written (n=%d)", len(combined))

    combined = pd.concat([prev, pd.DataFrame(new_rows)], ignore_index=True)
    combined.to_parquet(OUT, index=False)
    log.info("done: wrote %d rows to %s", len(combined), OUT)
    if skipped:
        log.warning("skipped %d MAs not in Pairwise70 loader: %s",
                    len(skipped), skipped[:5])


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=None,
                   help="cap D1 size for smoke runs")
    args = p.parse_args()
    main(limit=args.limit)
