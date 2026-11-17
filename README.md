# FOOTBALL-PROBABILITY-LAB

Open, reproducible football analytics research using Python and Google Colab.

The lab compares Poisson and Dixon–Coles score models, builds transparent match probabilities, and evaluates them with chronological out-of-sample tests. It covers club football and senior national-team A internationals, with men's and women's competitions kept separate.

## Research principles

- Evidence first: every dataset records its source, stated license, retrieval time, and transformations.
- No data leakage: a prediction may only use information available before its match.
- Reproducibility: notebooks, parameters, code versions, and evaluation windows are recorded.
- Separate populations: club, men's national teams, and women's national teams are modeled and evaluated separately.
- No invented data: sample files are templates, not historical observations.
- A positive expected value is an estimate, not a guarantee of profit.

## Project status

- [x] Repository initialized and Python CI tests passing.
- [x] Canonical match validation and national-team eligibility filters.
- [x] Source registry with license and coverage notes.
- [x] Reproducible download and normalization pipeline.
- [ ] Run ingestion and inspect the downloaded data manifest in Colab.
- [ ] Verify FIFA A-international status and regulation-time scores.
- [ ] Poisson and Dixon–Coles models.
- [ ] Walk-forward evaluation and calibration.
- [ ] Odds normalization, EV, Kelly, ROI and P/L.
- [ ] Live-match state model.

A feature is marked complete only after its tests pass and its methodology is documented. Dataset ingestion is not considered complete until the generated manifest and row-level audit have been reviewed.

## Quick start

Python 3.10+ is recommended.

    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    pytest

## Dataset format

See docs/DATA_DICTIONARY.md and docs/DATA_SOURCES.md. The canonical template is data/templates/matches_template.csv.

National-team FIFA A status must be yes, no, or unknown. Only exact, evidence-backed FIFA archive registry matches are considered verified. Unknown is never treated as yes.

## Google Colab

- Dataset schema audit: notebooks/01_dataset_audit_colab.ipynb
- Download and normalize sources: notebooks/02_ingest_datasets_colab.ipynb

## Data licensing

Code licensing and dataset licensing are different. Raw and processed data are not committed by default. ODC-BY attribution applies to the club source; men's international data is stated as CC0 1.0; women's international data uses the Unlicense. See docs/DATA_SOURCES.md and each source's own repository before redistribution.

## Roadmap

See docs/ROADMAP.md for staged implementation and acceptance criteria.
