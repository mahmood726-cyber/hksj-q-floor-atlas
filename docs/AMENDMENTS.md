# Amendments to spec.md

## Amendment 1 — Q=0 subset handling (2026-05-12)

**Trigger:** Empirical finding from Task 17 full D₁ compute (commit `00f72b0`).

**Issue:** Spec §1.4 defines `ci_width_ratio = floored / unfloored`. For the n=141 MAs (3.83% of D₁) where `Q = 0` exactly, the un-floored HKSJ multiplier `sqrt(Q/(k-1))` is exactly 0, so the un-floored CI width is 0 and the ratio is undefined (formally infinite).

**Resolution:**

1. The engine (`src/diff_engine.py`) now flags these rows with `is_q_zero=True` and assigns `ci_width_ratio = math.inf`. Property invariants (ratio ≥ 1, no sig_gain) still hold trivially.

2. The atlas (`outputs/atlas.csv`) splits D₁ into:
   - **D₁ᵃ** = D₁ ∩ {Q > 0}, n=3,536. The ratio summary (median, IQR, 95th percentile) and `pct_sig_loss` are computed on this subset and reported as the primary headline.
   - **D₁ᵇ** = D₁ ∩ {Q = 0}, n=141. Reported as a separate row with `n_q_zero` + `pct_sig_loss_q_zero`; the ratio is reported as "unbounded".

3. The headline narrative in the paper notes that the Q=0 subset represents the strongest possible floor effect (un-floored SE is exactly 0 — confidence intervals collapse to a point) and that the median ratio on D₁ᵃ is therefore a **conservative** estimate of the floor's impact.

**Rationale for amendment-not-spec-edit:** The spec was OTS-stamped concept-frozen with the D₁ definition (§1.3 says "I²=0 ∩ k≥2 ∩ converged"; nothing about Q>0). The Q=0 cases ARE in D₁ — they just need a separate reporting bucket. Editing spec.md to add a Q>0 filter would change the locked definition; an AMENDMENTS.md entry preserves the original definition and documents the empirical handling decision.

**Atlas impact:** The headline median CI-width ratio reported in `outputs/atlas.csv` is on D₁ᵃ (Q>0, n=3,536), not the full D₁ (n=3,677). The full D₁ count is preserved in the overall row's `n` column for reproducibility.
