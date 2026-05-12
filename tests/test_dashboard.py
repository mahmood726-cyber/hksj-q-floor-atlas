"""Tests for src.dashboard — offline HTML generation."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.dashboard import render_dashboard


@pytest.fixture
def atlas_df():
    return pd.DataFrame([
        {"stratum": "k=2", "n": 100, "median_ci_width_ratio": 1.7,
         "q25_ci_width_ratio": 1.4, "q75_ci_width_ratio": 2.1,
         "p95_ci_width_ratio": 3.2, "pct_sig_loss": 12.4},
        {"stratum": "k=3", "n": 80, "median_ci_width_ratio": 1.4,
         "q25_ci_width_ratio": 1.2, "q75_ci_width_ratio": 1.6,
         "p95_ci_width_ratio": 2.1, "pct_sig_loss": 8.1},
        {"stratum": "overall", "n": 3500, "median_ci_width_ratio": 1.5,
         "q25_ci_width_ratio": 1.2, "q75_ci_width_ratio": 1.9,
         "p95_ci_width_ratio": 2.8, "pct_sig_loss": 9.0},
    ])


@pytest.fixture
def per_ma_df():
    return pd.DataFrame([
        {"ma_id": f"M{i}", "k": 3 + i % 5,
         "ci_width_ratio": 1.1 + 0.1 * i, "sig_loss": i % 3 == 0,
         "ci_lo_unfloored": -0.1, "ci_hi_unfloored": 0.2,
         "ci_lo_floored": -0.15, "ci_hi_floored": 0.25,
         "estimate": 0.05}
        for i in range(20)
    ])


class TestRenderDashboard:
    def test_writes_index_html(self, atlas_df, per_ma_df, tmp_path):
        out_dir = tmp_path / "pages"
        render_dashboard(atlas_df, per_ma_df, out_dir)
        assert (out_dir / "index.html").exists()

    def test_no_external_cdn(self, atlas_df, per_ma_df, tmp_path):
        out_dir = tmp_path / "pages"
        render_dashboard(atlas_df, per_ma_df, out_dir)
        html = (out_dir / "index.html").read_text(encoding="utf-8")
        for forbidden in ["cdn.", "googleapis.", "jsdelivr.", "unpkg.",
                          "cloudflare.com", "http://", "https://cdn"]:
            assert forbidden not in html.lower(), f"forbidden URL: {forbidden}"

    def test_no_inline_javascript(self, atlas_df, per_ma_df, tmp_path):
        out_dir = tmp_path / "pages"
        render_dashboard(atlas_df, per_ma_df, out_dir)
        html = (out_dir / "index.html").read_text(encoding="utf-8")
        assert "<script" not in html.lower()
        assert "javascript:" not in html.lower()
        assert "onclick=" not in html.lower()

    def test_no_local_path_leakage(self, atlas_df, per_ma_df, tmp_path):
        out_dir = tmp_path / "pages"
        render_dashboard(atlas_df, per_ma_df, out_dir)
        html = (out_dir / "index.html").read_text(encoding="utf-8")
        for leak in ["C:\\Users", "C:/Users", "/home/", str(tmp_path)]:
            assert leak not in html, f"local path leaked: {leak}"

    def test_no_bom(self, atlas_df, per_ma_df, tmp_path):
        out_dir = tmp_path / "pages"
        render_dashboard(atlas_df, per_ma_df, out_dir)
        raw = (out_dir / "index.html").read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf"), "BOM present"

    def test_renders_overall_row(self, atlas_df, per_ma_df, tmp_path):
        out_dir = tmp_path / "pages"
        render_dashboard(atlas_df, per_ma_df, out_dir)
        html = (out_dir / "index.html").read_text(encoding="utf-8")
        # The overall median ratio (1.5) should appear in the HTML
        assert "1.5" in html
        assert "3500" in html or "3,500" in html

    def test_renders_strata_table(self, atlas_df, per_ma_df, tmp_path):
        out_dir = tmp_path / "pages"
        render_dashboard(atlas_df, per_ma_df, out_dir)
        html = (out_dir / "index.html").read_text(encoding="utf-8")
        assert "k=2" in html and "k=3" in html

    def test_histogram_png_generated(self, atlas_df, per_ma_df, tmp_path):
        out_dir = tmp_path / "pages"
        render_dashboard(atlas_df, per_ma_df, out_dir)
        assert (out_dir / "assets" / "ratio_histogram.png").exists()

    def test_3_forest_pngs_generated(self, atlas_df, per_ma_df, tmp_path):
        out_dir = tmp_path / "pages"
        render_dashboard(atlas_df, per_ma_df, out_dir)
        forests = sorted((out_dir / "assets").glob("forest_*.png"))
        assert len(forests) == 3
