"""Render the offline Pages dashboard from atlas + per-MA outputs."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.dashboard import render_dashboard  # noqa: E402

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

ATLAS = ROOT / "outputs" / "atlas.csv"
PER_MA = ROOT / "outputs" / "per_ma_results.parquet"
PAGES = ROOT / "docs"


def main():
    atlas = pd.read_csv(ATLAS)
    per_ma = pd.read_parquet(PER_MA)
    render_dashboard(atlas, per_ma, PAGES)
    log.info("dashboard written to %s", PAGES)


if __name__ == "__main__":
    main()
