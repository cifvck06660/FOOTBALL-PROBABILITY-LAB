"""Download and normalize public football results into the lab schema.

Raw downloads and processed outputs stay local under data/ and are gitignored.
No third-party match data is committed by this pipeline.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import pandas as pd

from .sources import FIFA_ARCHIVE, SOURCE_CATALOG

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REGISTRY_PATH = PROJECT_ROOT / "data" / "reference" / "fifa_a_match_registry.csv"


def _parse_dates(values: pd.Series) -> pd.Series:
    """Parse ISO dates, timestamps, and integer YYYYMMDD values safely."""
    if pd.api.types.is_numeric_dtype(values):
        as_text = values.astype("Int64").astype("string")
        parsed = pd.to_datetime(as_text, format="%Y%m%d", errors="coerce", utc=True)
    else:
        parsed = pd.to_datetime(values, errors="coerce", utc=True)
    return parsed.dt.strftime("%Y-%m-%d")


def _date_window(frame: pd.DataFrame, since: str, until: str) -> pd.DataFrame:
    dates = pd.to_datetime(frame["date"], errors="coerce", utc=True)
    start = pd.Timestamp(since, tz="UTC")
    end = pd.Timestamp(until, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    return frame.loc[dates.between(start, end)].copy()


def _match_id(source: str, date: str, home: str, away: str, competition: str) -> str:
    key = "|".join(
        str(value).strip().casefold()
        for value in (source, date, home, away, competition)
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]


def _competition_type(value: object) -> str:
    text = str(value).strip().casefold()
    if "friendly" in text:
        return "friendly"
    if "nation league" in text or "nations league" in text:
        return "nations_league"
    if "qualif" in text:
        return "qualification"
    return "other"


def _neutral_values(values: pd.Series) -> pd.Series:
    mapping = {
        "true": True, "1": True, "yes": True,
        "false": False, "0": False, "no": False,
    }
    return values.astype("string").str.strip().str.casefold().map(mapping)


def _canonical_frame(
    frame: pd.DataFrame,
    *,
    source_name: str,
    match_type: str,
    team_level: str,
    gender: str | None,
    competition_column: str,
    competition_type_column: str | None = None,
    home_score_column: str,
    away_score_column: str,
    neutral_column: str | None,
    competition_type_fn: Callable[[object], str],
    score_basis: str,
    model_eligible_90m: bool,
    fifa_status: str | None,
) -> pd.DataFrame:
    result = pd.DataFrame(index=frame.index)
    result["date"] = frame["date"]
    result["home_team"] = frame["home_team"].astype("string").str.strip()
    result["away_team"] = frame["away_team"].astype("string").str.strip()
    result["home_goals"] = pd.to_numeric(frame[home_score_column], errors="coerce")
    result["away_goals"] = pd.to_numeric(frame[away_score_column], errors="coerce")
    result["competition"] = frame[competition_column].astype("string").str.strip()
    result["match_type"] = match_type
    result["team_level"] = team_level
    type_values = frame[competition_type_column] if competition_type_column else frame[competition_column]
    result["competition_type"] = type_values.map(competition_type_fn)
    result["score_basis"] = score_basis
    result["model_eligible_90m"] = model_eligible_90m
    result["data_source"] = source_name

    if gender is not None:
        result["gender"] = gender
    if fifa_status is not None:
        result["fifa_a_match_status"] = fifa_status
    if neutral_column is not None and neutral_column in frame.columns:
        result["neutral_venue"] = _neutral_values(frame[neutral_column])
    else:
        result["neutral_venue"] = pd.NA

    valid = (
        result["date"].notna()
        & result["home_team"].notna()
        & result["away_team"].notna()
        & result["competition"].notna()
        & result["home_goals"].notna()
        & result["away_goals"].notna()
        & result["home_goals"].ge(0)
        & result["away_goals"].ge(0)
        & result["home_goals"].mod(1).eq(0)
        & result["away_goals"].mod(1).eq(0)
    )
    result = result.loc[valid].copy()
    result["home_goals"] = result["home_goals"].astype("int64")
    result["away_goals"] = result["away_goals"].astype("int64")
    result["match_id"] = [
        _match_id(source_name, row.date, row.home_team, row.away_team, row.competition)
        for row in result.itertuples()
    ]
    return result.reset_index(drop=True)


def normalize_club_results(
    source: pd.DataFrame, *, since: str, until: str
) -> pd.DataFrame:
    """Normalize club results, retaining regulation-time (full_time == F) only."""
    required = {
        "date", "home", "away", "gh", "ga", "competition", "full_time", "level"
    }
    missing = sorted(required - set(source.columns))
    if missing:
        raise ValueError("Club source is missing columns: " + ", ".join(missing))

    frame = source.copy()
    frame["date"] = _parse_dates(frame["date"])
    frame["full_time"] = frame["full_time"].astype("string").str.strip().str.upper()
    frame = frame.loc[frame["full_time"].eq("F")].copy()
    frame = frame.rename(columns={"home": "home_team", "away": "away_team"})
    frame = _date_window(frame, since, until)

    def club_type(value: object) -> str:
        level = str(value).strip().casefold()
        if level == "national":
            return "league"
        if level == "international":
            return "club_international_cup"
        return "other"

    normalized = _canonical_frame(
        frame,
        source_name="schochastics/football-data",
        match_type="club",
        team_level="senior",
        gender=None,
        competition_column="competition",
        competition_type_column="level",
        home_score_column="gh",
        away_score_column="ga",
        neutral_column=None,
        competition_type_fn=lambda value: (
            "league" if str(value).strip().casefold() == "national"
            else "club_international_cup" if str(value).strip().casefold() == "international"
            else "other"
        ),
        score_basis="regulation_90",
        model_eligible_90m=True,
        fifa_status=None,
    )
    return normalized


def normalize_mens_internationals(
    source: pd.DataFrame, *, since: str, until: str
) -> pd.DataFrame:
    """Normalize men's full-international candidates; FIFA status stays unknown."""
    required = {
        "date", "home_team", "away_team", "home_score", "away_score", "tournament"
    }
    missing = sorted(required - set(source.columns))
    if missing:
        raise ValueError("Men's source is missing columns: " + ", ".join(missing))

    frame = source.copy()
    frame["date"] = _parse_dates(frame["date"])
    frame = _date_window(frame, since, until)
    return _canonical_frame(
        frame,
        source_name="martj42/international_results",
        match_type="national_team",
        team_level="senior",
        gender="men",
        competition_column="tournament",
        home_score_column="home_score",
        away_score_column="away_score",
        neutral_column="neutral",
        competition_type_fn=_competition_type,
        score_basis="full_time_extra_time_included",
        model_eligible_90m=False,
        fifa_status="unknown",
    )


def normalize_womens_internationals(
    source: pd.DataFrame, *, since: str, until: str
) -> pd.DataFrame:
    """Normalize women's candidates conservatively; age level and FIFA status unknown."""
    required = {
        "date", "home_team", "away_team", "home_score", "away_score", "tournament"
    }
    missing = sorted(required - set(source.columns))
    if missing:
        raise ValueError("Women's source is missing columns: " + ", ".join(missing))

    frame = source.copy()
    frame["date"] = _parse_dates(frame["date"])
    frame = _date_window(frame, since, until)
    return _canonical_frame(
        frame,
        source_name="martj42/womens-international-results",
        match_type="national_team",
        team_level="unknown",
        gender="women",
        competition_column="tournament",
        home_score_column="home_score",
        away_score_column="away_score",
        neutral_column="neutral",
        competition_type_fn=_competition_type,
        score_basis="full_time_extra_time_included",
        model_eligible_90m=False,
        fifa_status="unknown",
    )


def _registry_key(row: object) -> tuple[str, str, str, str, str]:
    return (
        str(row.date).strip()[:10],
        str(row.home_team).strip().casefold(),
        str(row.away_team).strip().casefold(),
        str(row.competition).strip().casefold(),
        str(row.gender).strip().casefold(),
    )


def apply_fifa_a_registry(
    matches: pd.DataFrame, registry: pd.DataFrame | None
) -> pd.DataFrame:
    """Set FIFA A status only for exact, evidence-backed registry matches.

    Unmatched records remain unknown. A registry entry must carry a source URL
    and an explicit yes/no status; the function never infers status from names.
    """
    result = matches.copy()
    if "fifa_a_match_status" not in result.columns:
        result["fifa_a_match_status"] = "unknown"
    if registry is None or registry.empty:
        return result

    required = {
        "date", "home_team", "away_team", "competition", "gender",
        "fifa_a_match_status", "fifa_archive_url",
    }
    missing = sorted(required - set(registry.columns))
    if missing:
        raise ValueError("FIFA registry is missing columns: " + ", ".join(missing))

    verified: dict[tuple[str, str, str, str, str], str] = {}
    for row in registry.itertuples(index=False):
        status = str(row.fifa_a_match_status).strip().casefold()
        url = str(row.fifa_archive_url).strip()
        if status not in {"yes", "no"} or not url.startswith("https://"):
            continue
        verified[_registry_key(row)] = status

    for idx, row in result.iterrows():
        if row.get("match_type") != "national_team":
            continue
        key = (
            str(row["date"])[:10],
            str(row["home_team"]).strip().casefold(),
            str(row["away_team"]).strip().casefold(),
            str(row["competition"]).strip().casefold(),
            str(row.get("gender", "unknown")).strip().casefold(),
        )
        if key in verified:
            result.at[idx, "fifa_a_match_status"] = verified[key]
    return result


def download_file(url: str, destination: Path) -> str:
    """Download a source file and return its SHA-256 digest."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url, headers={"User-Agent": "football-probability-lab/0.1"}
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
    if not payload:
        raise RuntimeError(f"Downloaded empty file from {url}")
    destination.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def run_ingestion(since: str, until: str) -> dict:
    """Download, normalize, and write local candidate datasets plus a manifest."""
    if pd.Timestamp(since) > pd.Timestamp(until):
        raise ValueError("since must be on or before until")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    outputs: dict[str, pd.DataFrame] = {}
    source_log: dict[str, dict] = {}
    adapters = {
        "club": ("games.parquet", normalize_club_results),
        "men": ("men_results.csv", normalize_mens_internationals),
        "women": ("women_results.csv", normalize_womens_internationals),
    }

    for source_key, (filename, adapter) in adapters.items():
        metadata = SOURCE_CATALOG[source_key]
        raw_path = RAW_DIR / filename
        digest = download_file(metadata["raw_url"], raw_path)
        if metadata["format"] == "parquet":
            raw = pd.read_parquet(raw_path)
        else:
            raw = pd.read_csv(raw_path)

        normalized = adapter(raw, since=since, until=until)
        outputs[source_key] = normalized
        source_log[source_key] = {
            "name": metadata["name"],
            "repository": metadata["repository"],
            "raw_url": metadata["raw_url"],
            "license": metadata["license"],
            "license_url": metadata["license_url"],
            "coverage_claimed_by_source": metadata["coverage"],
            "raw_sha256": digest,
            "raw_rows": int(len(raw)),
            "normalized_rows_in_window": int(len(normalized)),
            "model_eligible_90m_rows": int(
                normalized["model_eligible_90m"].astype(bool).sum()
            ),
            "fifa_a_verified_rows": int(
                normalized.get(
                    "fifa_a_match_status", pd.Series(dtype="string")
                ).astype("string").eq("yes").sum()
            ),
            "limitations": metadata["limitations"],
        }

    registry = None
    if REGISTRY_PATH.exists():
        registry = pd.read_csv(REGISTRY_PATH)
    outputs["men"] = apply_fifa_a_registry(outputs["men"], registry)
    outputs["women"] = apply_fifa_a_registry(outputs["women"], registry)
    for key in ("men", "women"):
        source_log[key]["fifa_a_verified_rows"] = int(
            outputs[key]["fifa_a_match_status"].astype("string").eq("yes").sum()
        )

    filenames = {
        "club": "club_matches_10y.csv",
        "men": "national_men_candidates_10y.csv",
        "women": "national_women_candidates_10y.csv",
    }
    for key, filename in filenames.items():
        outputs[key].to_csv(PROCESSED_DIR / filename, index=False)

    combined = pd.concat(outputs.values(), ignore_index=True, sort=False)
    combined.to_csv(PROCESSED_DIR / "combined_candidates_10y.csv", index=False)

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "date_window_inclusive": {"since": since, "until": until},
        "fifa_archive_reference": FIFA_ARCHIVE,
        "sources": source_log,
        "outputs": {
            key: {
                "file": filename,
                "rows": int(len(outputs[key])),
            }
            for key, filename in filenames.items()
        },
        "combined_rows": int(len(combined)),
        "important_note": (
            "Candidate records are not automatically FIFA A internationals. "
            "National-team FIFA status remains unknown unless an exact match "
            "is present in the evidence-backed FIFA registry. National-team "
            "source scores include extra time and are not eligible for a "
            "90-minute model without separate regulation-time score evidence."
        ),
    }
    (PROCESSED_DIR / "ingestion_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and normalize public football datasets locally."
    )
    parser.add_argument("--since", default="2016-11-17")
    parser.add_argument("--until", default="2026-11-17")
    args = parser.parse_args()
    manifest = run_ingestion(args.since, args.until)
    print(json.dumps({
        "date_window": manifest["date_window_inclusive"],
        "outputs": manifest["outputs"],
        "combined_rows": manifest["combined_rows"],
        "processed_directory": str(PROCESSED_DIR),
    }, indent=2))


if __name__ == "__main__":
    main()
