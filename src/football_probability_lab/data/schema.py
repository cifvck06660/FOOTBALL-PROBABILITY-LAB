"""Canonical match dataset schema."""

REQUIRED_COLUMNS = (
    "match_id",
    "date",
    "home_team",
    "away_team",
    "home_goals",
    "away_goals",
    "competition",
    "match_type",
    "team_level",
    "competition_type",
)

ALLOWED_VALUES = {
    "match_type": {"club", "national_team"},
    "team_level": {"senior", "u23", "u20", "u17", "reserve", "unknown"},
    "competition_type": {
        "league",
        "cup",
        "qualification",
        "friendly",
        "nations_league",
        "other",
    },
    "gender": {"men", "women", "mixed", "unknown"},
    "fifa_a_match_status": {"yes", "no", "unknown"},
}

OPTIONAL_COLUMNS = (
    "season",
    "gender",
    "neutral_venue",
    "fifa_a_match_status",
    "data_source",
    "source_match_id",
)
