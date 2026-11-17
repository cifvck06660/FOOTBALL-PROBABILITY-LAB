"""Dataset schemas, ingestion, validation, and eligibility filters."""

from .ingestion import (
    apply_fifa_a_registry,
    normalize_club_results,
    normalize_mens_internationals,
    normalize_womens_internationals,
    run_ingestion,
)
from .validation import (
    ValidationReport,
    model_eligible_90m_matches,
    national_team_eligible_matches,
    validate_matches,
)

__all__ = [
    "ValidationReport",
    "apply_fifa_a_registry",
    "model_eligible_90m_matches",
    "national_team_eligible_matches",
    "normalize_club_results",
    "normalize_mens_internationals",
    "normalize_womens_internationals",
    "run_ingestion",
    "validate_matches",
]
