<!-- sentinel:skip-file — pre-registration record with URLs and archival paths. -->
# HKSJ Q-Floor Atlas — Pre-registration record

**Tag:** `prereg-v0.0.1`
**Date:** 2026-05-12
**Repository:** https://github.com/mahmood726-cyber/hksj-q-floor-atlas

---

## Locked artefacts (frozen at this tag)

| Artefact | Path | SHA-256 (where applicable) |
|---|---|---|
| Design spec | `docs/spec.md` | (computed at tag time; see git blob hash) |
| Input parquet | `data/inputs/full_method_results.parquet` | `31434fb118c6ec44a025eeb43a90e35ef9e050711fa45aa2cb5c1244b2d89751` |
| Goldens fixture | `tests/fixtures/golden_mas.json` | (computed at tag time; see git blob hash) |
| Amendments | `docs/AMENDMENTS.md` | Entry 1 records the Q=0 split decision |

The spec text itself is the canonical contract. The input parquet SHA is also pinned in `spec.md` §1.5 item 1.

## Pre-registration mechanisms used

### 1. Immutable git tag (primary)

`prereg-v0.0.1` is pushed to GitHub. Once pushed, the tag is part of the public commit graph and any modification is publicly detectable via SHA mismatch. This is the strongest practical pre-registration anchor in this session.

### 2. Internet Archive snapshot (secondary, independent timestamp)

Snapshots posted to web.archive.org are time-stamped by a third party independent of GitHub.

| URL | Wayback snapshot |
|---|---|
| `https://github.com/mahmood726-cyber/hksj-q-floor-atlas/blob/prereg-v0.0.1/docs/spec.md` | https://web.archive.org/web/20260512142257/https://github.com/mahmood726-cyber/hksj-q-floor-atlas/blob/prereg-v0.0.1/docs/spec.md |
| `https://github.com/mahmood726-cyber/hksj-q-floor-atlas/tree/prereg-v0.0.1` | https://web.archive.org/web/20260512142439/https://github.com/mahmood726-cyber/hksj-q-floor-atlas/tree/prereg-v0.0.1 |
| `https://github.com/mahmood726-cyber/hksj-q-floor-atlas/blob/prereg-v0.0.1/tests/fixtures/golden_mas.json` | https://web.archive.org/web/20260512142518/https://github.com/mahmood726-cyber/hksj-q-floor-atlas/blob/prereg-v0.0.1/tests/fixtures/golden_mas.json |
| `https://github.com/mahmood726-cyber/hksj-q-floor-atlas/blob/prereg-v0.0.1/data/inputs/full_method_results.sha256` | https://web.archive.org/web/20260512142650/https://github.com/mahmood726-cyber/hksj-q-floor-atlas/blob/prereg-v0.0.1/data/inputs/full_method_results.sha256 |

### 3. Bitcoin OTS stamp — ACTIVE (submitted; Bitcoin attestation pending)

`docs/spec.md`, `data/inputs/full_method_results.sha256`, and `tests/fixtures/golden_mas.json` were OTS-stamped on 2026-05-12 via the WSL Ubuntu Python 3.12 toolchain (matching the ARAC workaround precedent in [[lessons_ots_python313_windows]]). The native Windows Python 3.13 `ots` CLI continues to fail at import time per `opentimestamps-client 0.7.2 + python-bitcoinlib SSL loader looks for legacy libeay32.dll`.

Submitted to 4 OpenTimestamps calendar servers:
- `https://a.pool.opentimestamps.org`
- `https://b.pool.opentimestamps.org`
- `https://a.pool.eternitywall.com`
- `https://ots.btc.catallaxy.com`

Receipt files committed alongside originals:
- `docs/spec.md.ots`
- `data/inputs/full_method_results.sha256.ots`
- `tests/fixtures/golden_mas.json.ots`

The stamps are in "pending" state until a Bitcoin block confirms them (typically 12–48 hours after submission). To upgrade later: `wsl ~/.local/bin/ots upgrade <file>.ots`; then `ots verify <file>.ots` will report the Bitcoin block hash + height. Once upgraded, the receipt files should be re-committed with the upgraded payload (the SHA-256 of each .ots file will change after upgrade).

This adds a Bitcoin-anchored timestamp on top of the git-tag + IA-snapshot pair, completing the three-source pre-registration (git, IA, Bitcoin).

### 2b. v0.1.0 IA snapshots

| URL | Wayback snapshot |
|---|---|
| `https://mahmood726-cyber.github.io/hksj-q-floor-atlas/` (Pages) | https://web.archive.org/web/20260512143042/https://mahmood726-cyber.github.io/hksj-q-floor-atlas/ |
| `https://github.com/mahmood726-cyber/hksj-q-floor-atlas/blob/v0.1.0/outputs/atlas.csv` | https://web.archive.org/web/20260512143059/https://github.com/mahmood726-cyber/hksj-q-floor-atlas/blob/v0.1.0/outputs/atlas.csv |
| `https://github.com/mahmood726-cyber/hksj-q-floor-atlas/blob/v0.1.0/CHANGELOG.md` | https://web.archive.org/web/20260512143110/https://github.com/mahmood726-cyber/hksj-q-floor-atlas/blob/v0.1.0/CHANGELOG.md |

## Replication contract

Anyone with this repo + the `prereg-v0.0.1` tag + access to a Pairwise70 corpus + cochrane-modern-re can:

1. Verify `data/inputs/full_method_results.parquet` SHA matches the value pinned in `spec.md` §1.5 item 1.
2. Run `python analysis/00_preflight.py` and expect `PREFLIGHT OK`.
3. Run `pytest tests -v` and expect 64 tests pass.
4. Run `python analysis/01_compute_unfloored.py` then `02_build_atlas.py` and expect a numerically identical `outputs/atlas.csv` to the one tagged at `v0.1.0`.
5. Compare to `outputs/atlas.csv` at the `v0.1.0` tag.

## Headline that was pre-specified vs. computed

Pre-specified in spec.md §0 (before any compute on D₁): expected D₁ ≈ 3,500 MAs (57.6% of corpus); reporting median CI-width ratio + IQR + 95th pct + sig_loss rate.

Computed at v0.1.0:
- D₁ = 3,677 (matches the spec band exactly)
- D₁ᵃ (Q>0, n=3,536): median 3.64×, IQR 1.60–10.56, 95th pct 57.4×, sig_loss 17.08%
- D₁ᵇ (Q=0, n=141 = 3.83% of D₁): sig_loss 24.82%, ratio unbounded — see AMENDMENTS.md#1

The headline magnitude (3.64× median) is much larger than the controller's initial methods-note placeholder (1.5×); this is an empirical finding, not a HARK violation, because the spec only fixed the metric definition, not the expected value.
