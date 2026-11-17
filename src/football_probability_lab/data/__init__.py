"""Dataset schemas, validation, and eligibility filters."""

from .validation import (
    ValidationReport,
    national_team_eligible_matches,
    validate_matches,
)

__all__ = [
    "ValidationReport",
    "national_team_eligible_matches",
    "validate_matches",
]
