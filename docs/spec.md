<!-- sentinel:skip-file — this document contains absolute local paths
     as descriptive content (data locations, project layouts, release
     checklists), not application configuration. Same legitimate-paths-
     as-data pattern as E156/rewrite-workbook.txt and africa-tb-atlas. -->
# hksj-q-floor-atlas — Design Spec

**Date:** 2026-05-12
**Status:** Brainstorming complete; spec under user review before transition to writing-plans skill.
**Source idea:** New gap project; HKSJ Q-floor under-application at Pairwise70 scale.
**Sister projects** (template / reuse source):
- `cochrane-modern-re v0.1.0` — engine source; provides floored HKSJ values, REML τ², study-level loader.
- `repro-floor-atlas v0.1.0` — Pairwise70 effect ledger; precedent for atlas-shape outputs.
- `responder-floor-atlas v0.3.0` — pre-registration + amendment template.
- `africa-tb-atlas v0.1.0` — spec format template; 4-gate funnel pattern adapted to single-binary classification.

---

## 0. Summary

The HKSJ Q-Floor Atlas quantifies the **internal impact** of the Q-floor in HKSJ-pooled meta-analyses across the Pairwise70 corpus (n=6,386 Cochrane CDSR MAs, REML τ²). When `Q ≤ k−1` — mathematically equivalent to `I² = 0` — the canonical Hartung-Knapp-Sidik-Jonkman standard error narrows below the REML+Wald SE; advanced-stats.md and Cochrane Handbook v6.5 §10.10.4.3 (Nov 2024) require applying `max(1, Q/(k−1))` as a floor. The atlas reads `cochrane-modern-re/outputs/full_method_results.parquet` (which already applies the floor via `se_final = max(HKSJ_SE, Wald_SE)` in `run_metafor.R:54-67`), recomputes the **un-floored** HKSJ CIs for the I²=0 subset (~3,500 MAs after k≥2 and convergence filtering), and reports three headline metric groups stratified by k: (1) CI-width ratio distribution (floored ÷ un-floored) — median, IQR, 95th percentile; (2) significance-loss rate (unfloored CI excludes null, floored CI does not); (3) by-k counts of the floor-applicable denominator. Note: in the I²=0 regime the floor can only widen CIs, so "significance gain" is mathematically impossible and "sign flip" reduces to the same set as significance-loss — only one verdict flip exists. The atlas does **not** claim any specific published Cochrane CI is wrong; that's deferred to v0.2 when published-CI matching becomes feasible. Pre-registered via signed GitHub tag (`prereg-v0.0.1`) + IA snapshot + Bitcoin OTS of the spec and input parquet SHA-256. Target: Synthēsis Methods Note ≤400w at v0.1.0.

---

## 1. Scope and analytical contract

### 1.1 Project name and location

- **Name:** `hksj-q-floor-atlas`
- **Local path:** `C:\Projects\hksj-q-floor-atlas\`
- **GitHub:** `github.com/mahmood726-cyber/hksj-q-floor-atlas` (public)
- **Pages:** `mahmood726-cyber.github.io/hksj-q-floor-atlas/`

### 1.2 Headline question

> *Across the Pairwise70 Cochrane corpus, in the I²=0 regime where HKSJ-no-floor narrows the SE below REML+Wald, what is the distribution of the precision overstatement (CI-width ratio), and how often does applying the Q-floor flip the significance verdict or the directional conclusion?*

### 1.3 Denominator and numerator

| Symbol | Definition | Expected count |
|---|---|---|
| D₀ | Pairwise70 MAs in cochrane-modern-re full_method_results, `method='REML_HKSJ_PI' & converged==True` | 6,386 − non-converged ≈ 6,332 |
| D₁ (primary) | D₀ ∩ `{i2 == 0.0 & k_effective >= 2}` | ~3,500 (extrapolated from 3,677 I²=0 rows; minus k=1 and convergence) |
| D₂ (secondary, "near-floor") | D₀ ∩ `{0 < i2 <= 25 & k_effective >= 2}` | ~1,000 (descriptive only) |

**Numerators** are four impact metrics computed on D₁ (defined in §1.4).

### 1.4 Headline metrics

For each MA in D₁, compute:

- `ci_width_unfloored = ci_hi_unfloored − ci_lo_unfloored`
- `ci_width_floored = ci_hi_floored − ci_lo_floored`
- `ci_width_ratio = ci_width_floored / ci_width_unfloored`  (must be `≥ 1.0` by construction in the I²=0 regime; property-tested)
- `sig_unfloored = (ci_lo_unfloored > 0) OR (ci_hi_unfloored < 0)`
- `sig_floored = (ci_lo_floored > 0) OR (ci_hi_floored < 0)`
- `sig_loss = sig_unfloored AND (NOT sig_floored)`  (one-directional: floor can only widen, so significance can only be lost, never gained)

Mathematical note: in the I²=0 regime, `HKSJ_SE_unfloored ≤ Wald_SE = HKSJ_SE_floored`, so the floored CI strictly contains the unfloored CI. This means `sig_gain` (unfloored not significant → floored significant) is impossible by construction, and any directional "sign flip" reduces to `sig_loss`. v0.1 reports only `sig_loss`; the impossibility of `sig_gain` is property-tested.

For each k-stratum in `{2, 3, 4-5, 6-9, ≥10}`:
- `n_in_stratum`
- median `ci_width_ratio`, IQR, 95th percentile
- `pct_sig_loss`

Overall headline (D₁ pooled):
- Median `ci_width_ratio` + IQR + 95th percentile
- Overall `pct_sig_loss`
- `n_floor_applicable` and percent of D₀

### 1.5 Locked-at-spec decisions (HARK protection)

These freeze on `prereg-v0.0.1` tag + IA snapshot + Bitcoin OTS-stamp. Any change → AMENDMENTS.md entry, new tag, new OTS stamp.

1. **Input parquet:** `cochrane-modern-re/outputs/full_method_results.parquet` at SHA-256 `31434fb118c6ec44a025eeb43a90e35ef9e050711fa45aa2cb5c1244b2d89751`.
2. **Study-level data source:** `cochrane-modern-re.src.loaders.iter_mas_with_log()` reading from `PAIRWISE70_DIR` env var; the Pairwise70 corpus checksum is treated as cochrane-modern-re's contract (their pre-reg covers it).
3. **τ² estimator:** REML only. PM, SJ, Bayesian explicitly deferred to v0.2.
4. **HKSJ degrees of freedom:** t-distribution with `df = k − 1`. Matches advanced-stats.md and cochrane-modern-re. Not `qnorm`.
5. **Null point:** 0 on the cochrane-modern-re log/standardised scale (every Pairwise70 effect is log-RR, log-OR, log-HR, SMD, or MD; cochrane-modern-re harmonises to scales where 0 = null).
6. **I²=0 detection:** strict equality `i2 == 0.0` in the input parquet. I² ∈ (0, 25] flagged as D₂ "near-floor" descriptive secondary; NOT in primary headline.
7. **Convergence:** only `converged == True` rows enter D₀. Non-convergent excluded with `reason_code` preserved.
8. **k floor:** `k_effective >= 2`. HKSJ undefined at k=1; excluded by definition.
9. **k strata:** `{2, 3, 4-5, 6-9, ≥10}` — boundaries frozen pre-extraction.
10. **Significance test:** two-sided 95% CI excludes null point ⇒ significant. p-values not separately recomputed.
11. **Verdict flip:** v0.1 reports `sig_loss` only (unfloored significant → floored not significant). `sig_gain` is mathematically impossible in I²=0 regime (floor only widens) and is property-tested to never occur; observing one is a ship-blocker bug.
12. **atlas.csv shape:** 1 row per (stratum, metric_group) × 5 strata + 1 overall = ≤6 rows × ≤8 cols.
13. **Tolerance:** `ci_width_ratio < 1.0 − 1e-9` is a ship-blocker (mathematically impossible in I²=0; indicates implementation bug).
14. **Golden MAs (n=3):** pre-selected pre-extraction by smallest k in the I²=0 subset; hand-verified against `metafor::rma(..., test="knha")` R reference within 1e-6 on `estimate`, `se`, `ci_lo`, `ci_hi`.
15. **Pre-ship validation gate:** pytest 100% pass on all tests, Sentinel BLOCK=0, 3 goldens match, property test on full D₁ passes, Pages renders the required artefacts (§1.8).
16. **Bitcoin OTS-stamp:** `spec.md` + input parquet SHA-256 + 3-golden expected values stamped via `ots` before any unfloored compute runs.
17. **IA snapshot:** spec.md + atlas.csv (at tag time) archived to web.archive.org; URLs recorded in `docs/preregistration.md`.

### 1.6 Non-goals (NOT in v0.1.0)

- **No claim** that any specific published Cochrane CI is wrong. Published-CI matching is v0.2.
- **No PM, SJ, or Bayesian τ²** — lean v0.1 scope per user decision 2026-05-12.
- **No NMA** — Pairwise70 is pairwise only.
- **No DL re-pooling** — DL's I²=0 rate (63.8%) reported as a descriptive secondary in the discussion; not in the headline.
- **No editorial recommendations** beyond "Cochrane Handbook v6.5 and RevMan-2025 already specify the floor."
- **No multi-arm correction** — Pairwise70 single-comparison contracts inherited.

### 1.7 Engineering reuse

| Component | Source | Reuse mode |
|---|---|---|
| Floored HKSJ values, REML τ², I², `k_effective`, `converged` | `cochrane-modern-re/outputs/full_method_results.parquet` | Read-only SHA-pinned copy in `data/inputs/`. |
| Study-level effect data per MA | `cochrane-modern-re.src.loaders.iter_mas_with_log()` reading `PAIRWISE70_DIR` | Python import dep; cochrane-modern-re pip-installed editable. |
| metafor R harness | `cochrane-modern-re/src/r_scripts/run_metafor.R` | Forked to `src/r_scripts/hksj_unfloored.R`; the `max(HKSJ_SE, Wald_SE)` block at lines 54–67 is **removed** to expose raw HKSJ SE. |
| Spec format + pre-reg pattern | africa-tb-atlas, responder-floor-atlas, pactr-hiddenness-atlas | Template. |
| Sentinel pre-push hook | `C:\Sentinel\` | Install before first push. |
| OTS workflow | malaria-ct-recon, responder-floor-atlas | Bitcoin OTS via `ots stamp` (workaround for Python 3.13 bug per lessons.md: use Python 3.11/3.12 alongside, or web stamper). |

### 1.8 Ship gates

All required for `v0.1.0` tag:

- pytest: ≥80 tests, 100% pass, 0 unintended skips on primary path.
- Sentinel: BLOCK=0 (P0 + P1 clean) at `python -m sentinel scan --repo C:\Projects\hksj-q-floor-atlas`.
- Property test on D₁: `ci_width_ratio >= 1.0 − 1e-9` for every row.
- 3 golden MAs match `metafor::rma(..., test="knha")` reference within 1e-6 on `estimate`, `se`, `ci_lo`, `ci_hi`.
- Pages renders: (a) headline numbers banner, (b) k-strata table, (c) CI-ratio histogram with log-x, (d) 3 worked-example forest plots showing floor vs no-floor CIs.
- `paper/methods_note.md` ≤ 400 words (Synthēsis cap; word-count gate enforced in CI).
- IA snapshot of spec.md (at prereg tag) and atlas.csv (at v0.1.0 tag) with URLs recorded.
- Bitcoin OTS-stamp of `spec.md` + input parquet SHA-256 + golden expected values before any compute.

### 1.9 Failure modes / fail-closed conditions

- Input parquet SHA mismatch → fail at load with diff vs pinned hash.
- `full_method_results.parquet` missing or unreadable → fail at load, surface user-action ("re-run cochrane-modern-re or restore from backup").
- `PAIRWISE70_DIR` env var unset → fail at load, surface user-action.
- Study-level data missing for any D₁ row → fail at load with the offending `ma_id` list.
- Unfloored compute non-convergence rate > 5% of D₁ → halt, surface for inspection (cochrane-modern-re primary run was 162/19,158 ≈ 0.85% non-convergence; our subset should be similar).
- `ci_width_ratio < 1.0 − 1e-9` anywhere in D₁ → halt, treat as implementation bug (this is mathematically impossible in I²=0).
- `methods_note.md` word count > 400 → ship-blocker until trimmed.
- Sentinel BLOCK > 0 → ship-blocker.

### 1.10 Workbook + portfolio integration

- E156 workbook entry: next sequence number after current (check `C:\E156\rewrite-workbook.txt` count at v0.1.0 tag time).
- INDEX.md: new row under Active Projects (Atlases).
- MEMORY.md pointer: new line under Active Projects (top 8 — individual files).
- MEMORY/hksj-q-floor-atlas.md: created after tag.
- `C:\ProjectIndex\agent-records\restart-manifest.json`: incremented projectCount.
- Sentinel install: pre-push hook before first push.
- Long-term-plan: add as completed entry once shipped.

---

## 2. Deliverables (v0.1.0)

- `docs/spec.md` (this document; frozen at `prereg-v0.0.1`).
- `docs/preregistration.md` (IA + OTS records, golden expected values).
- `docs/AMENDMENTS.md` (any post-prereg changes).
- `outputs/atlas.csv` (k-strata + overall headline).
- `outputs/per_ma_results.parquet` (per-MA floored + unfloored + impact flags).
- `paper/methods_note.md` (≤400w Synthēsis target).
- `paper/E156-PROTOCOL.md` (E156 7-sentence body).
- Pages site at `mahmood726-cyber.github.io/hksj-q-floor-atlas/` with dashboard.
- `tests/` ≥80 pytest tests.
- `CHANGELOG.md`, `CITATION.cff`, `LICENSE` (MIT).

---

## 3. Tag chain

- `prereg-v0.0.1` — spec.md + input SHA + golden expected values, Bitcoin-OTS, IA-snapshot. No compute yet.
- `v0.1.0` — atlas.csv + paper draft + Pages + Zenodo DOI candidate. All ship gates pass.

---

## 4. Open questions deferred to the plan

These are NOT spec-locked; they're plan-level decisions deferred to the writing-plans phase:

- Exact pytest count target (≥80 stated; final count emerges from plan).
- Exact dashboard chart library (Pages constraint: offline + no CDN).
- Exact CI-width-ratio histogram bin edges.
- Exact selection rule for the 3 golden MAs (currently "smallest k in I²=0 subset"; plan should add deterministic tiebreaker).
- Whether to publish per-MA parquet on Pages (size + privacy review).
