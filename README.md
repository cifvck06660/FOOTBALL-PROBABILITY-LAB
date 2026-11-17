# FOOTBALL-PROBABILITY-LAB

Open, reproducible football analytics research using Python and Google Colab.

The lab will compare Poisson and Dixon–Coles score models, build transparent match probabilities, and evaluate them with chronological out-of-sample tests. It covers club football and senior national-team A internationals, with men's and women's competitions kept separate.

## Research principles

- Evidence first: every dataset must record its source, retrieval date, license, and transformations.
- No data leakage: a prediction may only use information available before its match.
- Reproducibility: notebooks, parameters, code versions, and evaluation windows are recorded.
- Separate populations: club, men's national teams, and women's national teams are modeled and evaluated separately.
- No invented data: sample files are templates, not historical observations.
- A positive expected value is an estimate, not a guarantee of profit.

## Project status

- [x] Repository initialized.
- [x] Python package and automated test workflow scaffolded.
- [ ] Dataset validation: awaiting first CI run and review.
- [ ] Historical club dataset ingestion.
- [ ] Senior national-team A-international dataset ingestion.
- [ ] Poisson attack/defence maximum-likelihood estimation.
- [ ] Dixon–Coles rho estimation.
- [ ] Walk-forward evaluation and calibration.
- [ ] Odds normalization, EV, Kelly, ROI and P/L evaluation.
- [ ] Live-match state model.

A feature is marked complete only after its tests pass and its methodology is documented.

## Quick start

Python 3.10+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
pytest
```

## Dataset format

See [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) and [data/templates/matches_template.csv](data/templates/matches_template.csv).

Required fields:

`match_id,date,home_team,away_team,home_goals,away_goals,competition,match_type,team_level,competition_type`

For national-team records, `fifa_a_match_status` must be `yes`, `no`, or `unknown`. Only verified senior A internationals are eligible for the A-international dataset. Unknown status is not silently treated as eligible.

### National-team scope

- Senior men's and senior women's teams are stored and analyzed separately.
- Include only first teams representing national associations; exclude U-23, U-20, U-17, B teams, and league selections.
- Store FIFA A-international recognition explicitly as evidence-backed metadata.
- Keep friendlies separately labeled from competitive fixtures. The analysis can include or exclude friendlies explicitly.
- Do not infer FIFA recognition solely from team names or tournament labels.

## Google Colab

Open [notebooks/01_dataset_audit_colab.ipynb](notebooks/01_dataset_audit_colab.ipynb) in Google Colab. The notebook clones this public repository, installs the package, and lets you upload a CSV for validation.

## Data licensing

Code licensing and dataset licensing are different. Do not commit third-party raw datasets unless their license permits redistribution. Keep source URLs, license terms, attribution, retrieval date, and transformation notes with each dataset. Raw data is ignored by Git by default.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for staged implementation and acceptance criteria.
