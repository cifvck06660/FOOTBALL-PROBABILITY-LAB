import pandas as pd

from football_probability_lab.data.ingestion import (
    apply_fifa_a_registry,
    normalize_club_results,
    normalize_mens_internationals,
    normalize_womens_internationals,
)
from football_probability_lab.data.validation import (
    model_eligible_90m_matches,
    validate_matches,
)


def test_club_import_keeps_only_regulation_time_matches():
    source = pd.DataFrame(
        [
            {
                "date": "2020-01-01",
                "home": "Home FC",
                "away": "Away FC",
                "gh": 2,
                "ga": 1,
                "competition": "Example League",
                "full_time": "F",
                "level": "national",
            },
            {
                "date": "2020-01-02",
                "home": "Cup Home",
                "away": "Cup Away",
                "gh": 3,
                "ga": 2,
                "competition": "Continental Cup",
                "full_time": "E",
                "level": "international",
            },
            {
                "date": "2020-01-03",
                "home": "Shootout Home",
                "away": "Shootout Away",
                "gh": 5,
                "ga": 4,
                "competition": "Cup",
                "full_time": "P",
                "level": "international",
            },
        ]
    )
    result = normalize_club_results(
        source, since="2020-01-01", until="2020-12-31"
    )
    assert len(result) == 1
    assert result.loc[0, "score_basis"] == "regulation_90"
    assert bool(result.loc[0, "model_eligible_90m"])
    assert result.loc[0, "competition_type"] == "league"


def test_mens_source_is_candidate_not_auto_fifa_a_or_90m_eligible():
    source = pd.DataFrame(
        [
            {
                "date": "2020-01-01",
                "home_team": "Country A",
                "away_team": "Country B",
                "home_score": 1,
                "away_score": 0,
                "tournament": "Friendly",
                "neutral": False,
            }
        ]
    )
    result = normalize_mens_internationals(
        source, since="2019-01-01", until="2021-01-01"
    )
    assert result.loc[0, "team_level"] == "senior"
    assert result.loc[0, "fifa_a_match_status"] == "unknown"
    assert result.loc[0, "score_basis"] == "full_time_extra_time_included"
    assert not bool(result.loc[0, "model_eligible_90m"])
    assert result.loc[0, "competition_type"] == "friendly"


def test_womens_source_is_conservatively_unverified():
    source = pd.DataFrame(
        [
            {
                "date": "2020-01-01",
                "home_team": "Country A",
                "away_team": "Country B",
                "home_score": 2,
                "away_score": 1,
                "tournament": "Women's Tournament",
                "neutral": "TRUE",
            }
        ]
    )
    result = normalize_womens_internationals(
        source, since="2019-01-01", until="2021-01-01"
    )
    assert result.loc[0, "team_level"] == "unknown"
    assert result.loc[0, "gender"] == "women"
    assert result.loc[0, "fifa_a_match_status"] == "unknown"
    assert not bool(result.loc[0, "model_eligible_90m"])


def test_fifa_registry_requires_exact_record_and_https_evidence():
    matches = pd.DataFrame(
        [
            {
                "date": "2020-01-01",
                "home_team": "Country A",
                "away_team": "Country B",
                "competition": "Friendly",
                "gender": "men",
                "match_type": "national_team",
                "fifa_a_match_status": "unknown",
            }
        ]
    )
    registry = pd.DataFrame(
        [
            {
                "date": "2020-01-01",
                "home_team": "Country A",
                "away_team": "Country B",
                "competition": "Friendly",
                "gender": "men",
                "fifa_a_match_status": "yes",
                "fifa_archive_url": "https://inside.fifa.com/data-centre/matches",
            }
        ]
    )
    verified = apply_fifa_a_registry(matches, registry)
    assert verified.loc[0, "fifa_a_match_status"] == "yes"

    registry.loc[0, "fifa_archive_url"] = "not-a-url"
    unverified = apply_fifa_a_registry(matches, registry)
    assert unverified.loc[0, "fifa_a_match_status"] == "unknown"


def test_model_eligibility_requires_regulation_time_score():
    frame = pd.DataFrame(
        [
            {
                "match_id": "club-1",
                "date": "2020-01-01",
                "home_team": "A",
                "away_team": "B",
                "home_goals": 1,
                "away_goals": 0,
                "competition": "League",
                "match_type": "club",
                "team_level": "senior",
                "competition_type": "league",
                "score_basis": "regulation_90",
                "model_eligible_90m": True,
            },
            {
                "match_id": "int-1",
                "date": "2020-01-02",
                "home_team": "C",
                "away_team": "D",
                "home_goals": 2,
                "away_goals": 1,
                "competition": "Friendly",
                "match_type": "national_team",
                "team_level": "senior",
                "competition_type": "friendly",
                "score_basis": "full_time_extra_time_included",
                "model_eligible_90m": False,
                "fifa_a_match_status": "unknown",
            },
        ]
    )
    result = model_eligible_90m_matches(frame)
    assert result["match_id"].tolist() == ["club-1"]
    report = validate_matches(frame)
    assert report.is_valid
