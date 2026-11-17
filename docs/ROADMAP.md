# Development roadmap

A stage is complete only when its acceptance criteria are met, tests pass, and the method is documented. Download code being present does not mean that data ingestion has been run or that source records have been verified.

## Stage 1 — Data foundation
- [x] Initialize repository, package layout, and CI test workflow.
- [x] Validate canonical match CSV schema and row integrity (GitHub Actions passed).
- [x] Record source repositories, stated licenses, coverage, and limitations.
- [x] Add reproducible download and normalization adapters for club, men's international, and women's international datasets.
- [x] Keep friendly and competitive national-team records separately labeled.
- [ ] Run the download pipeline in Google Colab and inspect the generated manifest.
- [ ] Verify senior men's FIFA A-international rows against the FIFA archive.
- [ ] Verify senior women's FIFA A-international rows against the FIFA archive.
- [ ] Obtain regulation-time scores for national-team records before 90-minute goal modeling.
- [ ] Review duplicates, team aliases, and competition mappings.

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
