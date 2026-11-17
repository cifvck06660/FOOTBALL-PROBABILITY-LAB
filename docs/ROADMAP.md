# Development roadmap

A stage is complete only when its acceptance criteria are met, tests pass, and the method is documented. Do not mark work green based on file creation alone.

## Stage 1 — Data foundation
- [x] Initialize repository, package layout, and CI test workflow.
- [x] Validate canonical match CSV schema and row integrity (GitHub Actions passed on 2026-11-17).
- [ ] Add source/license/retrieval metadata manifest.
- [ ] Ingest a licensed historical club dataset.
- [ ] Ingest verified senior men's national-team A internationals.
- [ ] Ingest verified senior women's national-team A internationals.
- [ ] Keep friendly and competitive fixtures separately filterable.
- [ ] Add deduplication and team-name mapping review.

## Stage 2 — Baseline models
- [ ] Poisson attack/defence model with home advantage, fitted by maximum likelihood.
- [ ] Time weighting and explicit training cutoff.
- [ ] Dixon–Coles low-score correction.
- [ ] Estimate rho from training data; do not hard-code it.
- [ ] Separate club, men's national, and women's national model populations.

## Stage 3 — Validation and backtesting
- [ ] Expanding-window walk-forward evaluation.
- [ ] Log Loss and Brier Score.
- [ ] Calibration bins and reliability diagrams.
- [ ] Compare Poisson and Dixon–Coles on identical out-of-sample fixtures.
- [ ] Report uncertainty and sample sizes.

## Stage 4 — Odds and market evaluation
- [ ] Odds source/license and timestamp audit.
- [ ] Remove bookmaker margin using documented method.
- [ ] 1X2, totals, Asian handicap, correct score, double chance, team totals, odd/even.
- [ ] EV, Kelly, ROI, P/L, and closing-line value with realistic settlement rules.

## Stage 5 — Live model
- [ ] Minute-by-minute match state and score state.
- [ ] Red-card and goal-time event data.
- [ ] In-play handicap and totals line snapshots.
- [ ] Separate first-half, second-half, 10-minute, and 15-minute evaluations.
