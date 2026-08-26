"""Canonical faculty special-role values and normalization helpers."""

import re


SPECIAL_ROLES = (
    "FA",
    "AA",
    "Project Incharge",
    "TC",
    "Placement Coordinator",
    "Others",
    "None",
)

SPECIAL_ROLE_WORKLOAD_ROLES = frozenset(SPECIAL_ROLES[:5])

_ROLE_PATTERNS = (
    ("FA", ("faculty advisor", r"\bfa\b")),
    ("AA", ("academic advisor", r"\baa\b")),
    (
        "Project Incharge",
        ("project coordinator", "project panel head", "project incharge"),
    ),
    ("TC", ("time table", "timetable", r"\btc\b")),
    (
        "Placement Coordinator",
        ("placement coordinator", "placement member", "placement training"),
    ),
)


def normalize_special_role(value):
    """Normalize one raw role cell using the required precedence."""

    if value is None:
        return "None"

    normalized = str(value).strip()
    if not normalized or normalized.casefold() in {"none", "nil", "null"}:
        return "None"

    lowered = normalized.casefold()
    for role, patterns in _ROLE_PATTERNS:
        if any(
            re.search(pattern, lowered)
            for pattern in patterns
        ):
            return role

    return "Others"