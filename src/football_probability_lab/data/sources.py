"""Public football data source registry and known limitations."""

SOURCE_CATALOG = {
    "club": {
        "name": "schochastics/football-data",
        "repository": "https://github.com/schochastics/football-data",
        "raw_url": "https://raw.githubusercontent.com/schochastics/football-data/master/data/results/games.parquet",
        "license": "Open Data Commons Attribution License 1.0 (ODC-BY 1.0)",
        "license_url": "https://opendatacommons.org/licenses/by/1-0/",
        "coverage": "1888-2023",
        "format": "parquet",
        "limitations": [
            "Source README reports 1,237,935 matches in 207 top-tier domestic leagues and 20 international club tournaments.",
            "Scores include extra time and penalties; use full_time == F only for regulation-time modeling.",
            "Source author warns that older records may contain errors and historical club identities may be inconsistent.",
            "Latest stated coverage ends in 2023; it does not complete the requested rolling ten-year window through 2026.",
            "ODC-BY attribution is required."
        ],
    },
    "men": {
        "name": "martj42/international_results",
        "repository": "https://github.com/martj42/international_results",
        "raw_url": "https://raw.githubusercontent.com/martj42/international_results/master/results.csv",
        "license": "CC0 1.0 Universal",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "coverage": "1872-2024 (as stated in repository README)",
        "format": "csv",
        "limitations": [
            "Repository describes the records as men's full internationals and excludes B teams, U-23 teams and league selections.",
            "The source includes friendly matches and some non-FIFA tournaments; this is not proof that every row is a FIFA A international.",
            "Scores include extra time but exclude penalty shootouts; no regulation-time score field is supplied.",
            "FIFA A status is initialized as unknown and must be verified against the FIFA archive before inclusion in the FIFA A dataset.",
            "CC0 1.0 is stated by the source repository."
        ],
    },
    "women": {
        "name": "martj42/womens-international-results",
        "repository": "https://github.com/martj42/womens-international-results",
        "raw_url": "https://raw.githubusercontent.com/martj42/womens-international-results/master/results.csv",
        "license": "Unlicense",
        "license_url": "https://unlicense.org/",
        "coverage": "Work in progress; repository README reports 11,020 results and says many matches are missing",
        "format": "csv",
        "limitations": [
            "The repository says major tournament results should be complete but many matches, especially friendlies, are missing.",
            "The README does not establish that every row is a senior A international; team_level is initialized as unknown.",
            "Scores include extra time but no regulation-time score field is supplied.",
            "FIFA A status is initialized as unknown and must be verified against the FIFA archive.",
            "The source repository uses the Unlicense."
        ],
    },
}

FIFA_ARCHIVE = {
    "name": "FIFA International Match Archive",
    "url": "https://inside.fifa.com/data-centre/matches",
    "purpose": "Authoritative reference for manual or future automated FIFA A-international verification.",
    "limitations": [
        "FIFA says match details vary in completeness and are being added over time.",
        "The archive is described by FIFA as historical and illustrative; do not assume it provides a complete downloadable bulk dataset."
    ],
}
