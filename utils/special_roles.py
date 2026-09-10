"""Canonical faculty special-role values and normalization helpers."""

import re


SPECIAL_ROLES = (
    "FA",
    "AA",
    "TC",
    "Placement Coordinator",
    "Project Incharge",
    "Others",
    "None",
)

SPECIAL_ROLE_WORKLOAD_ROLES = frozenset(SPECIAL_ROLES[:5])

_CANONICAL_ROLES = {role.casefold(): role for role in SPECIAL_ROLES}

_ROLE_PATTERNS = (
    ("FA", re.compile(r"\b(?:faculty\s+advis(?:or|er)|fa)\b")),
    ("AA", re.compile(r"\b(?:academic\s+advis(?:or|er)|aa)\b")),
    ("TC", re.compile(
        r"\b(?:time\s*table\s+(?:coordinator|coordiantor|committee\s+member)|"
        r"tt\s+coordinator|tc)\b"
    )),
    ("Placement Coordinator", re.compile(
        r"\b(?:placement\s+(?:coordinator|member|training\s+coordinator|"
        r"cell\s+coordinator|incharge))\b"
    )),
    ("Project Incharge", re.compile(
        r"\b(?:project\s+(?:coordinator|incharge|panel\s+head|panel\s+member))\b"
    )),
)


def normalize_special_role(value):
    """Normalize a raw role cell into an ordered, comma-separated role list."""

    if value is None:
        return "None"

    normalized = re.sub(r"[^a-z0-9]+", " ", str(value).casefold()).strip()
    if not normalized or normalized in {"none", "nil", "null"}:
        return "None"

    matches = []
    for role, pattern in _ROLE_PATTERNS:
        match = pattern.search(normalized)
        if match:
            matches.append((match.start(), role))

    roles = {role for _, role in matches}
    if roles:
        return ",".join(role for role in SPECIAL_ROLES if role in roles)

    return "Others"


def special_role_list(value):
    """Return canonical roles from legacy or comma-separated stored values."""

    normalized = normalize_special_role(value)
    return normalized.split(",") if normalized != "None" else []


def normalize_submitted_special_roles(value):
    """Validate and normalize roles submitted by the faculty forms."""

    if value is None:
        values = []
    elif isinstance(value, (list, tuple, set)):
        values = value
    elif isinstance(value, str):
        values = value.split(",")
    else:
        raise ValueError("Invalid special role.")

    roles = set()
    for item in values:
        if not isinstance(item, str):
            raise ValueError("Invalid special role.")
        role = _CANONICAL_ROLES.get(item.strip().casefold())
        if role is None:
            raise ValueError("Invalid special role.")
        roles.add(role)

    roles.discard("None") if len(roles) > 1 else None
    if not roles:
        return "None"
    return ",".join(role for role in SPECIAL_ROLES if role in roles)