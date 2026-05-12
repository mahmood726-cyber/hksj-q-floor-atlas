# When the Q-floor matters: HKSJ precision overstatement at Pairwise70 scale

**Authors:** [STUDENT REWRITER, first author]¹; Mahmood Ahmad²,³ (middle); [SUPERVISING FACULTY, last/senior author]¹.

**Affiliations:**
¹ [first/senior author institution].
² Tahir Heart Institute, Rabwah, Pakistan.
³ ORCID: 0000-0001-9107-3704.

**Corresponding author:** [first author] <[first author email]>.

**Reporting checklist:** PRISMA 2020.
**Code:** https://github.com/mahmood726-cyber/hksj-q-floor-atlas (v0.1.0).
**Dashboard:** https://mahmood726-cyber.github.io/hksj-q-floor-atlas/.
**Pre-registration:** tag `prereg-v0.0.1` + Internet Archive snapshots recorded in `docs/preregistration.md`.

---

**Background.** The Hartung-Knapp-Sidik-Jonkman (HKSJ) confidence-interval adjustment is the RevMan-2025 default for random-effects meta-analyses with small k.¹,² Cochrane Handbook v6.5 §10.10.4.3 and advanced-stats convention require a `max(1, Q/(k−1))` floor on the HKSJ variance multiplier: when `Q ≤ k−1` — equivalently `I² = 0` — the un-floored HKSJ standard error narrows below the REML+Wald SE. Authors and software that omit the floor systematically overstate precision.

**Methods.** We audited the entire Pairwise70 Cochrane CDSR corpus (n = 6,386 MAs) via cochrane-modern-re's pre-pooled outputs (REML τ², HKSJ with floor; input parquet SHA-256 pinned in the pre-registered spec).³ For every MA with `I² = 0` and `k ≥ 2` (D₁ = 3,677; 57.6% of corpus) we recomputed the un-floored HKSJ CI via an independent metafor pass with the floor block removed. For each MA we derived the CI-width ratio (floored ÷ un-floored) and a significance-loss flag. The Q=0 subset (n=141; 3.8% of D₁), where the un-floored SE is exactly zero, is reported separately because the ratio is unbounded.

**Results.** On the well-defined D₁ᵃ subset (Q>0, n=3,536), the median CI-width ratio was **3.64×** (IQR 1.60–10.56; 95th percentile **57.4×**). Significance was lost in **17.08%** of D₁ᵃ. The effect was substantial across all k-strata (median ratios 3.10×–4.26×); significance-loss rates rose with k (8.6% at k=2; 25.1% at k≥10). The Q=0 subset (D₁ᵇ, n=141) lost significance in 24.8% with unbounded ratio. Mathematically required invariants — ratio ≥ 1, no sig-gain — held for every D₁ᵃ MA, confirming engine correctness against 3 hand-verified golden references at 1e-6 tolerance.

**Limitations.** v0.1 establishes prevalence and per-MA impact under our own re-pooling; we do not claim any specific published Cochrane CI is incorrect (published-CI matching is v0.2). Pairwise only; NMAs out of scope. Sensitivity to PM and Sidik-Jonkman τ² estimators is v0.2.

**Conclusion.** The HKSJ Q-floor is not a niche correction. It applies to 57.6% of the Cochrane CDSR; on the well-defined subset, omitting it overstates precision by a median factor of 3.64× and flips significance for ~1 in 6 MAs. RevMan-2025 already requires it; legacy R/Stata HKSJ code without the floor systematically inflates apparent confidence.

---

## References (Vancouver)

1. Hartung J, Knapp G. A refined method for the meta-analysis of controlled clinical trials with binary outcome. *Stat Med.* 2001;20(24):3875–3889. doi:10.1002/sim.1009
2. IntHout J, Ioannidis JPA, Borm GF. The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. *BMC Med Res Methodol.* 2014;14:25. doi:10.1186/1471-2288-14-25
3. Higgins JPT, Thomas J, Chandler J, Cumpston M, Li T, Page MJ, Welch VA, editors. *Cochrane Handbook for Systematic Reviews of Interventions*. Version 6.5 (updated August 2024). Cochrane; 2024. §10.10.4.3.

---

## Data availability

No patient-level data used. Analysis derived from publicly available aggregate trial-level data via the cochrane-modern-re v0.1.0 pipeline (Pairwise70 corpus). Input parquet SHA-256 pinned in `docs/spec.md` §1.5. All atlas outputs (`outputs/atlas.csv`, dashboard, paper) are reproducible at the v0.1.0 tag.

## Ethics

Not required. Secondary methodological analysis of publicly available aggregate data; no human participants; no patient-identifiable information; no individual-participant data.

## Funding

None.

## Competing interests

None declared.

## Author contributions (CRediT)

- [STUDENT REWRITER, first author] — Writing – original draft; Writing – review & editing; Validation.
- [SUPERVISING FACULTY, last/senior author] — Supervision; Validation; Writing – review & editing.
- Mahmood Ahmad (middle author, NOT first or last) — Conceptualization; Methodology; Software; Data curation.

## AI disclosure

Computational tooling (including AI-assisted coding via Claude Code [Anthropic]) was used to develop the analysis pipeline. Final manuscript is human-written, reviewed, and approved by the authors; submitted text is not AI-generated.

## Licence

Manuscript: CC-BY-4.0. Code: MIT.
