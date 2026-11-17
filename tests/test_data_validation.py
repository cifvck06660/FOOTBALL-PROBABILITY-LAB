import pandas as pd

from football_probability_lab.data import (
    national_team_eligible_matches,
    validate_matches,
)


def valid_frame():
    return pd.DataFrame(
        [
            {
                "match_id": "m-001",
                "date": "2024-06-01",
                "home_team": "Indonesia",
                "away_team": "Iraq",
                "home_goals": 0,
                "away_goals": 2,
                "competition": "World Cup Qualification",
                "match_type": "national_team",
                "team_level": "senior",
                "competition_type": "qualification",
                "gender": "men",
                "fifa_a_match_status": "yes",
            }
        ]
    )


def test_valid_dataset_passes():
    report = validate_matches(valid_frame())
    assert report.is_valid
    assert report.total_rows == 1
    assert report.valid_rows == 1


def test_missing_required_column_fails():
    frame = valid_frame().drop(columns=["home_goals"])
    report = validate_matches(frame)
    assert not report.is_valid
    assert any("home_goals" in error for error in report.errors)


def test_negative_goal_count_fails():
    frame = valid_frame()
    frame.loc[0, "home_goals"] = -1
    report = validate_matches(frame)
    assert not report.is_valid
    assert any("home_goals" in error for error in report.errors)


def test_duplicate_match_ids_fail():
    frame = pd.concat([valid_frame(), valid_frame()], ignore_index=True)
    report = validate_matches(frame)
    assert not report.is_valid
    assert any("duplicated IDs" in error for error in report.errors)


def test_only_verified_senior_a_internationals_are_eligible():
    frame = pd.concat([valid_frame()] * 4, ignore_index=True)
    frame.loc[1, "team_level"] = "u23"
    frame.loc[2, "fifa_a_match_status"] = "unknown"
    frame.loc[3, "competition_type"] = "friendly"

    all_a_matches = national_team_eligible_matches(frame)
    competitive_only = national_team_eligible_matches(
        frame, include_friendlies=False
    )

    assert len(all_a_matches) == 2
    assert len(competitive_only) == 1


def test_validation_does_not_modify_input():
    frame = valid_frame()
    before = frame.copy(deep=True)
    validate_matches(frame)
    pd.testing.assert_frame_equal(frame, before)
