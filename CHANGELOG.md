# Changelog

## [0.1.0] - 2026-05-12

### Headline

Across the Pairwise70 Cochrane CDSR corpus (n=6,386 MAs), the I²=0 subset where the HKSJ Q-floor applies is D₁ = **3,677 MAs (57.6%)**. On the well-defined D₁ᵃ subset (Q>0, n=3,536):

- median CI-width ratio (floored ÷ un-floored): **3.64×**
- IQR: **1.60×–10.56×**
- 95th percentile: **57.4×**
- significance lost: **17.08%**

D₁ᵇ (Q=0, n=141 = 3.83% of D₁): sig_loss 24.8%, ratio unbounded (un-floored HKSJ SE is exactly zero; floor effect is unbounded). See `docs/AMENDMENTS.md` entry 1 for the split-handling decision.

### Scope (per spec.md §1.5–§1.6)

- Lean v0.1: REML τ² only (no PM, SJ, or Bayesian)
- Internal impact only (no published-CI matching; that's v0.2)
- Pairwise only (no NMA)

### Engine

- Input: `cochrane-modern-re/outputs/full_method_results.parquet` SHA-256 `31434fb118c6ec44a025eeb43a90e35ef9e050711fa45aa2cb5c1244b2d89751`
- Un-floored HKSJ: independent R/metafor pass (`src/r_scripts/hksj_unfloored.R`) with the floor block removed
- 3 golden MAs hand-verified against an independent R reference at 1e-6 tolerance
- Property invariants enforced: `ci_width_ratio ≥ 1.0 − 1e-9` on D₁ᵃ; impossibility of `sig_gain` property-tested

### Ship gates

- pytest: **64 passed, 0 failed, 0 unintended skipped**
- Sentinel: **BLOCK=0, WARN=0, INFO=0**
- All 7 spec §1.8 gates PASS (see `docs/SHIP_READINESS.md`)

### Pre-registration

- `prereg-v0.0.1` git tag (immutable) pushed to GitHub
- 4 Internet Archive snapshots recorded in `docs/preregistration.md`
- Bitcoin OTS-stamp deferred (Python 3.13 SSL libeay32 bug per lessons.md; web-stamper fallback documented)

### Deliverables

- `outputs/atlas.csv` — 7 rows (5 k-strata + overall + Q=0)
- `outputs/per_ma_results.parquet` — per-MA detail (gitignored; regenerable)
- `pages/index.html + assets/*.png` — offline Pages dashboard
- `paper/methods_note.md` — 340 words (≤400 Synthēsis cap)
- `paper/E156-PROTOCOL.md` — 7 sentences, 146 words (≤156 cap)

## [0.0.1] - 2026-05-12

- Initial scaffold and spec.
- Preflight verified.
