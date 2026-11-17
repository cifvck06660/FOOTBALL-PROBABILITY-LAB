"""Validation helpers for normalized football match datasets."""

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from .schema import ALLOWED_VALUES, REQUIRED_COLUMNS


@dataclass(frozen=True)
class ValidationReport:
    """Machine-readable summary of a dataset validation run."""

    total_rows: int
    valid_rows: int
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["is_valid"] = self.is_valid
        return result


def validate_matches(frame: pd.DataFrame) -> ValidationReport:
    """Validate the canonical match table without modifying the input.

    This checks structure and basic integrity. It does not certify a source's
    historical accuracy or FIFA A-international status.
    """
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame")

    total = len(frame)
    errors: list[str] = []
    warnings: list[str] = []

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing_columns:
        errors.append("Missing required columns: " + ", ".join(missing_columns))
        return ValidationReport(total, 0, tuple(errors), tuple(warnings))

    if frame.empty:
        errors.append("Dataset contains no match rows.")
        return ValidationReport(0, 0, tuple(errors), tuple(warnings))

    bad_rows = pd.Series(False, index=frame.index)

    text_columns = (
        "match_id",
        "home_team",
        "away_team",
        "competition",
        "match_type",
        "team_level",
        "competition_type",
    )
    for column in text_columns:
        values = frame[column].astype("string").str.strip()
        invalid = values.isna() | values.eq("")
        count = int(invalid.sum())
        if count:
            errors.append(f"{column}: {count} blank or missing value(s).")
            bad_rows |= invalid

    parsed_dates = pd.to_datetime(frame["date"], errors="coerce", utc=True)
    invalid_dates = parsed_dates.isna()
    if invalid_dates.any():
        count = int(invalid_dates.sum())
        errors.append(f"date: {count} invalid or missing value(s).")
        bad_rows |= invalid_dates

    for column in ("home_goals", "away_goals"):
        numeric = pd.to_numeric(frame[column], errors="coerce")
        invalid = numeric.isna() | (numeric < 0) | (numeric % 1 != 0)
        count = int(invalid.sum())
        if count:
            errors.append(
                f"{column}: {count} value(s) must be non-negative whole numbers."
            )
            bad_rows |= invalid

    home = frame["home_team"].astype("string").str.strip().str.casefold()
    away = frame["away_team"].astype("string").str.strip().str.casefold()
    same_team = home.notna() & away.notna() & home.eq(away)
    if same_team.any():
        count = int(same_team.sum())
        errors.append(f"home_team/away_team: {count} match(es) have identical teams.")
        bad_rows |= same_team

    ids = frame["match_id"].astype("string").str.strip()
    duplicate_ids = ids.duplicated(keep=False) & ids.notna()
    if duplicate_ids.any():
        count = int(duplicate_ids.sum())
        errors.append(f"match_id: {count} row(s) belong to duplicated IDs.")
        bad_rows |= duplicate_ids

    for column, allowed in ALLOWED_VALUES.items():
        if column not in frame.columns:
            continue
        values = frame[column].astype("string").str.strip().str.casefold()
        present = values.notna() & values.ne("")
        invalid = present & ~values.isin(allowed)
        count = int(invalid.sum())
        if count:
            errors.append(
                f"{column}: {count} unsupported value(s); allowed: "
                + ", ".join(sorted(allowed))
                + "."
            )
            bad_rows |= invalid

    if "fifa_a_match_status" not in frame.columns:
        warnings.append(
            "fifa_a_match_status is absent; national-team A-international "
            "eligibility cannot be established."
        )
    else:
        national = (
            frame["match_type"].astype("string").str.strip().str.casefold()
            == "national_team"
        )
        unverified = national & (
            frame["fifa_a_match_status"]
            .astype("string")
            .str.strip()
            .str.casefold()
            .isin(["", "unknown"])
        )
        if unverified.any():
            warnings.append(
                f"{int(unverified.sum())} national-team row(s) have unverified "
                "FIFA A-international status."
            )

    if "model_eligible_90m" in frame.columns:
        eligible = (
            frame["model_eligible_90m"]
            .astype("string")
            .str.strip()
            .str.casefold()
            .eq("true")
        )
        if "score_basis" in frame.columns:
            wrong_score_basis = eligible & ~frame["score_basis"].astype(
                "string"
            ).str.strip().str.casefold().eq("regulation_90")
            if wrong_score_basis.any():
                count = int(wrong_score_basis.sum())
                errors.append(
                    f"model_eligible_90m: {count} row(s) are marked eligible "
                    "without regulation_90 score basis."
                )
                bad_rows |= wrong_score_basis
        if "fifa_a_match_status" in frame.columns:
            national = (
                frame["match_type"].astype("string").str.strip().str.casefold()
                == "national_team"
            )
            unverified_eligible = (
                eligible
                & national
                & ~frame["fifa_a_match_status"]
                .astype("string")
                .str.strip()
                .str.casefold()
                .eq("yes")
            )
            if unverified_eligible.any():
                count = int(unverified_eligible.sum())
                errors.append(
                    f"model_eligible_90m: {count} unverified national-team "
                    "row(s) are marked eligible."
                )
                bad_rows |= unverified_eligible

    valid_rows = int((~bad_rows).sum())
    if valid_rows < total:
        warnings.append(
            f"{total - valid_rows} row(s) contain one or more validation errors."
        )

    return ValidationReport(total, valid_rows, tuple(errors), tuple(warnings))


def national_team_eligible_matches(
    frame: pd.DataFrame, *, include_friendlies: bool = True
) -> pd.DataFrame:
    """Return verified senior national-team A internationals only."""
    required = {
        "match_type",
        "team_level",
        "fifa_a_match_status",
        "competition_type",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(
            "Missing columns needed for national-team filtering: "
            + ", ".join(missing)
        )

    normalized = {
        column: frame[column].astype("string").str.strip().str.casefold()
        for column in required
    }
    mask = (
        normalized["match_type"].eq("national_team")
        & normalized["team_level"].eq("senior")
        & normalized["fifa_a_match_status"].eq("yes")
    )
    if not include_friendlies:
        mask &= normalized["competition_type"].ne("friendly")

    return frame.loc[mask.fillna(False)].copy()


def model_eligible_90m_matches(frame: pd.DataFrame) -> pd.DataFrame:
    """Return only rows explicitly cleared for regulation-time goal modeling."""
    if "model_eligible_90m" not in frame.columns or "score_basis" not in frame.columns:
        raise ValueError(
            "model_eligible_90m and score_basis columns are required."
        )
    eligible = (
        frame["model_eligible_90m"]
        .astype("string")
        .str.strip()
        .str.casefold()
        .eq("true")
    )
    regulation = (
        frame["score_basis"]
        .astype("string")
        .str.strip()
        .str.casefold()
        .eq("regulation_90")
    )
    return frame.loc[(eligible & regulation).fillna(False)].copy()
