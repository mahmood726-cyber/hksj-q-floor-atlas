# Ship Readiness Report — v0.1.0 candidate

**Date:** 2026-05-12
**HEAD:** edc5b2a639d0bcff9e05292e8cf463bec845a604
**Status:** PASS — ready for Task 20 (OTS + IA + gh) and Task 25 (v0.1.0 tag).

## Gate results

| Gate | Status | Detail |
|---|---|---|
| pytest | PASS | 64 tests passed, 0 failed, 0 unintended skips |
| Sentinel BLOCK=0 | PASS | BLOCK=0, WARN=2 (P1-empty-dataframe-access in analysis/02_build_atlas.py:85 and src/dashboard.py:85 — both are guarded by upstream atlas construction that always produces an overall row) |
| Property: ratio ≥ 1 on D₁ᵃ | PASS | 0 violations in 3,536 rows |
| Property: no sig_gain | PASS | 0 violations in 3,677 rows |
| Dashboard renders | PASS | 1 histogram + 3 forest PNGs + index.html |
| Methods Note ≤ 400w | PASS | 340 words |
| E156-PROTOCOL 7 sentences ≤ 156w | PASS | 7 sentences, 146 words |

## Headline (for Task 25 release notes)

D₁ᵃ (Q>0, n=3,536):
- median CI-width ratio: 3.64×
- IQR: 1.60–10.56×
- 95th pct: 57.4×
- sig_loss: 17.08%

D₁ᵇ (Q=0): n=141 (3.83% of D₁), sig_loss 24.8%, ratio unbounded.

Total D₁: 3,677 / 6,386 = 57.6% of Pairwise70 corpus.

## Remaining manual tasks for v0.1.0

- **Task 20** (pre-registration):
  - Bitcoin OTS-stamp: `docs/spec.md`, `data/inputs/full_method_results.sha256`, `tests/fixtures/golden_mas.json`. CLI may break on Python 3.13; fallback is opentimestamps.org web stamper.
  - Create GitHub repo: `gh repo create mahmood726-cyber/hksj-q-floor-atlas --public --source=. --remote=origin`
  - Push master and tag `prereg-v0.0.1`
  - IA-snapshot spec.md + repo root
  - Record URLs in `docs/preregistration.md`

- **Task 25** (v0.1.0):
  - Update CHANGELOG.md v0.1.0 entry with the actual numbers
  - Tag `v0.1.0`, push tag
  - Enable GitHub Pages (gh api POST repos/.../pages with source.branch=master, source.path=/pages)
  - IA-snapshot atlas.csv + Pages
  - Record URLs in `docs/preregistration.md`

- **Task 26** (portfolio):
  - reconcile_counts.py run
  - Append to C:\E156\rewrite-workbook.txt
  - Add row to C:\ProjectIndex\INDEX.md
  - Create memory/hksj-q-floor-atlas.md + MEMORY.md pointer
  - Bump restart-manifest.json projectCount
