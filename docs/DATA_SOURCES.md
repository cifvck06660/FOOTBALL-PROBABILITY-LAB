# Data sources, licenses, and limitations

The ingestion script downloads source files at runtime. Raw and processed data are stored locally under data/raw and data/processed, which are gitignored. The repository commits source metadata and code, not third-party match dumps.

## Source registry

| Dataset | Source coverage stated by publisher | License stated by publisher | Intended use and caveats |
|---|---|---|---|
| Club results | 1,237,935 matches, 207 top-tier domestic leagues and 20 international club tournaments, 1888–2023 | ODC-BY 1.0 | Keep only rows with full_time = F for 90-minute goals. Source scores include extra time and penalties for E/P rows. Latest stated coverage ends in 2023. |
| Men's internationals | 49,459 matches, 1872–2024 (repository README) | CC0 1.0 | Source describes these as men's full internationals and excludes B/U23/league selections, but includes friendlies and some non-FIFA tournaments. FIFA A status remains unknown until exact verification. Scores include extra time. |
| Women's internationals | Work in progress; README reports 11,020 results and says many matches are missing | Unlicense | Major tournament coverage is described as mostly complete, but many fixtures are missing. Senior status and FIFA A status remain unknown until verified. Scores include extra time. |

### Primary source links

- Club dataset: https://github.com/schochastics/football-data
- Club results file: https://github.com/schochastics/football-data/blob/master/data/results/games.parquet
- Men's national-team dataset: https://github.com/martj42/international_results
- Men's results file: https://github.com/martj42/international_results/blob/master/results.csv
- Women's national-team dataset: https://github.com/martj42/womens-international-results
- Women's results file: https://github.com/martj42/womens-international-results/blob/master/results.csv
- FIFA International Match Archive: https://inside.fifa.com/data-centre/matches

## FIFA A-international verification

The men's dataset's phrase "full internationals" is not treated as identical to FIFA A-match recognition. It contains some non-FIFA tournaments. Every imported national-team row therefore starts with fifa_a_match_status = unknown.

Use data/reference/fifa_a_match_registry_template.csv to record exact evidence-backed matches. Copy it to data/reference/fifa_a_match_registry.csv and add a row only after checking the FIFA International Match Archive. The registry requires an exact date, home team, away team, competition, gender, explicit yes/no status, and HTTPS evidence URL. Unmatched rows remain unknown. Never infer FIFA A status from team names alone.

FIFA notes that archive match details vary in completeness and are being added over time. The archive is a verification reference, not assumed to be a complete downloadable bulk export.

## Score period and model eligibility

- Club source: full_time = F means the match ended in regulation time. Only those records are imported as score_basis = regulation_90 and model_eligible_90m = true. Extra-time and shootout rows are excluded.
- Men's internationals: source scores include extra time and do not provide a separate regulation-time score. Records are candidates only; model_eligible_90m = false.
- Women's internationals: source scores include extra time and do not provide a separate regulation-time score. Records are candidates only; model_eligible_90m = false.
- A national-team match can be verified as FIFA A and still remain ineligible for a 90-minute goal model until its regulation-time score is separately sourced.

## Rolling ten-year window

The default Colab run uses 2016-11-17 through 2026-11-17. Source availability does not cover the full window uniformly: the club dataset currently states coverage through 2023, and the men's dataset README states coverage through 2024. The women's dataset is explicitly incomplete. The ingestion manifest records actual downloaded row counts and observed date ranges. Missing years are not fabricated or silently filled.

## Reproducibility

Every run writes data/processed/ingestion_manifest.json with:
- UTC retrieval timestamp and date window;
- source repositories, raw URLs, stated licenses, and source SHA-256 hashes;
- raw and normalized row counts;
- source coverage claims and limitations.

The script prints no credentials and requires no API key.
