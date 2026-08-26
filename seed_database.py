import csv
import argparse
import re
from pathlib import Path

from config import db
from utils.special_roles import SPECIAL_ROLES, normalize_special_role

DATA_DIR = Path(__file__).resolve().parent / "data"

PROFESSOR_POSTS = {
    "professor": "Professor",
    "professor & head": "Professor & Head",
    "principal architect": "Principal Architect",
    "associate professor": "Associate Professor",
    "assistant professor": "Assistant Professor",
    "assistant professor - jr.g": "Assistant Professor - Jr.G",
    "research assistant professor": "Research Assistant Professor",
    "teaching associate": "Teaching Associate",
    "research scholar": "Research Scholar",
}

BUILDINGS = {
    "tp1": "TP1",
    "tp2": "TP2",
    "ub": "UB",
    "main block": "Main Block",
    "biotech": "Biotech",
    "i-mac lab": "I-MAC Lab",
}

FIELD_ALIASES = {
    "subject_code": ("subject_code", "subject code", "code"),
    "subject_name": ("subject_name", "subject name", "name"),
    "faculty_id": ("faculty_id", "faculty id", "faculty code"),
    "faculty_name": ("faculty_name", "faculty name", "name", "username"),
    "professor_post": ("professor_post", "professor post", "post"),
    "special_role": ("special_role", "special role", "role"),
    "cabin_no": ("cabin_no", "cabin number", "cabin"),
    "contact": ("contact", "phone", "phone number"),
    "email": ("email", "email address"),
    "regulation": ("regulation", "regulation year"),
    "program": ("program",),
    "department": ("department",),
    "semester": ("semester", "semester type"),
    "category": ("category",),
    "course_type": ("course_type", "course type", "type"),
    "credits": ("credits", "credit"),
    "hours_per_week": ("hours_per_week", "hours per week", "weekly hours"),
    "ltpc": ("ltpc", "ltpc value"),
    "batch": ("batch",),
    "section": ("section", "sections"),
    "room_number": ("room_number", "room number", "room", "room_no"),
    "building_name": ("building_name", "building name", "building"),
    "building": ("building", "building name", "building_name"),
    "room_no": ("room_no", "room number", "room", "room_number"),
    "main_faculty_id": ("main_faculty_id", "main faculty id"),
    "cofaculty_id": ("cofaculty_id", "cofaculty id"),
    "lab_slot": ("lab_slot", "lab slot", "slot"),
    "slot": ("slot", "theory slot", "lab slot"),
    "class_type": ("class_type", "class type"),
}

def normalize_nil(value):
    if value is None:
        return None
    value = str(value).strip()
    return None if not value or value.upper() in {"NIL", "NONE", "NULL", "NA", "N/A", "-"} else value

def normalize_professor_post(value):
    value = normalize_nil(value)
    return PROFESSOR_POSTS.get(value.casefold(), value) if value else None

def normalize_building(value):
    value = normalize_nil(value)
    return BUILDINGS.get(value.casefold(), value) if value else None

def normalize_merged_section(value):
    value = normalize_nil(value)
    if value is None:
        return None
    sections = re.split(r"\s*(?:,|/|&|\+|\band\b)\s*", value, flags=re.IGNORECASE)
    return ", ".join(dict.fromkeys(section.strip() for section in sections if section.strip()))

def normalize_semester(value):
    value = normalize_nil(value)
    if value is None:
        return None
    match = re.fullmatch(r"(?:semester\s*)?(\d+)", value, flags=re.IGNORECASE)
    return int(match.group(1)) if match else value

def _normalized_headers(fieldnames):
    return {str(field).strip().casefold(): field for field in fieldnames or []}

def _value(row, field):
    headers = _normalized_headers(row.keys())
    for alias in FIELD_ALIASES.get(field, (field,)):
        original = headers.get(alias.casefold())
        if original is not None:
            return normalize_nil(row.get(original))
    return None

def _read_csv(filename, key_fields, normalizer):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"Missing file: {path}")
        return []

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    normalized = [normalizer(row) for row in rows]
    seen = set()
    duplicates = 0
    for row in normalized:
        key = tuple(row.get(field) for field in key_fields)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)

    print(f"Rows loaded: {len(rows)}")
    print(f"Rows normalized: {len(normalized)}")
    print(f"Duplicate rows detected: {duplicates}")
    return normalized

def _subject_row(row):
    return {
        "subject_code": _value(row, "subject_code"),
        "subject_name": _value(row, "subject_name"),
        "regulation": _value(row, "regulation"),
        "program": _value(row, "program"),
        "department": _value(row, "department"),
        "semester": normalize_semester(_value(row, "semester")),
        "category": _value(row, "category"),
        "course_type": _value(row, "course_type"),
        "credits": _value(row, "credits"),
        "hours_per_week": _value(row, "hours_per_week"),
        "LTPC": _value(row, "ltpc"),
    }

def import_subject_master():
    return _read_csv("Subject_Master.csv", ("subject_code",), _subject_row)

def _faculty_row(row):
    return {
        "faculty_id": _value(row, "faculty_id"),
        "faculty_name": _value(row, "faculty_name"),
        "email": _value(row, "email"),
        "contact": _value(row, "contact"),
        "cabin_no": _value(row, "cabin_no"),
        "professor_post": normalize_professor_post(_value(row, "professor_post")) or "Assistant Professor",
        "special_role": normalize_special_role(_value(row, "special_role")),
    }

def import_faculty_master():
    return _read_csv("Faculty_Master.csv", ("faculty_id",), _faculty_row)

def _allocation_row(row, class_type):
    return {
        "faculty_id": _value(row, "faculty_id"),
        "subject_code": _value(row, "subject_code"),
        "subject_name": _value(row, "subject_name"),
        "batch": _value(row, "batch"),
        "section": normalize_merged_section(_value(row, "section")),
        "room_number": _value(row, "room_number"),
        "building_name": normalize_building(_value(row, "building_name")),
        "slot": _value(row, "slot"),
        "class_type": class_type,
    }

def import_theory_allocations():
    return _read_csv(
        "Theory_Allocations.csv",
        ("faculty_id", "subject_code", "batch", "section", "slot"),
        lambda row: _allocation_row(row, "theory"),
    )

def import_lab_allocations():
    def lab_row(row):
        return {
            "main_faculty_id": _value(row, "main_faculty_id"),
            "cofaculty_id": _value(row, "cofaculty_id"),
            "subject_code": _value(row, "subject_code"),
            "batch": _value(row, "batch"),
            "section": normalize_merged_section(_value(row, "section")),
            "lab_slot": _value(row, "lab_slot"),
            "building": _value(row, "building"),
            "room_no": _value(row, "room_no"),
        }

    return _read_csv(
        "Lab_Allocations.csv",
        ("main_faculty_id", "subject_code", "batch", "section", "lab_slot"),
        lab_row,
    )


def _duplicate_count(rows):
    seen = set()
    duplicates = 0
    for row in rows:
        key = tuple(sorted(row.items()))
        if key in seen:
            duplicates += 1
        seen.add(key)
    return duplicates


def _missing_optional(rows, fields):
    return sum(
        1
        for row in rows
        for field in fields
        if row.get(field) is None
    )


def _validation_errors(faculties, subjects, theory, labs):
    errors = []
    faculty_ids = {row.get("faculty_id") for row in faculties if row.get("faculty_id")}
    subject_codes = {row.get("subject_code") for row in subjects if row.get("subject_code")}
    email_rows = {}
    for row_number, row in enumerate(faculties, 2):
        if row.get("email"):
            email_rows.setdefault(row["email"].casefold(), []).append(row_number)
    for email, row_numbers in email_rows.items():
        if len(row_numbers) > 1:
            errors.append(
                "Faculty_Master.csv rows "
                f"{', '.join(map(str, row_numbers))}: duplicate email {email}"
            )

    for row_number, row in enumerate(faculties, 2):
        for field in ("faculty_id", "faculty_name"):
            if not row.get(field):
                errors.append(f"Faculty_Master.csv row {row_number}: missing {field}")
        if row.get("professor_post") not in PROFESSOR_POSTS.values():
            errors.append(f"Faculty_Master.csv row {row_number}: invalid professor_post")
        if row.get("special_role") not in SPECIAL_ROLES:
            errors.append(f"Faculty_Master.csv row {row_number}: invalid special_role")

    for row_number, row in enumerate(subjects, 2):
        if not row.get("subject_code"):
            errors.append(f"Subject_Master.csv row {row_number}: missing subject_code")

    for row_number, row in enumerate(theory, 2):
        for field in ("faculty_id", "subject_code"):
            if not row.get(field):
                errors.append(f"Theory_Allocations.csv row {row_number}: missing {field}")
        if row.get("faculty_id") and row["faculty_id"] not in faculty_ids:
            errors.append(f"Theory_Allocations.csv row {row_number}: unresolved faculty_id {row['faculty_id']}")
        if row.get("subject_code") and row["subject_code"] not in subject_codes:
            errors.append(f"Theory_Allocations.csv row {row_number}: unresolved subject_code {row['subject_code']}")
        if row.get("batch"):
            try:
                int(row["batch"])
            except ValueError:
                errors.append(f"Theory_Allocations.csv row {row_number}: invalid batch {row['batch']}")

    for row_number, row in enumerate(labs, 2):
        for field in ("main_faculty_id", "subject_code"):
            if not row.get(field):
                errors.append(f"Lab_Allocations.csv row {row_number}: missing {field}")
        for field in ("main_faculty_id", "cofaculty_id"):
            if row.get(field) and row[field] not in faculty_ids:
                errors.append(f"Lab_Allocations.csv row {row_number}: unresolved {field} {row[field]}")
        if row.get("subject_code") and row["subject_code"] not in subject_codes:
            errors.append(f"Lab_Allocations.csv row {row_number}: unresolved subject_code {row['subject_code']}")

    return errors


def load_import_data():
    data = {
        "faculty": import_faculty_master(),
        "subjects": import_subject_master(),
        "theory": import_theory_allocations(),
        "labs": import_lab_allocations(),
    }
    data["errors"] = _validation_errors(
        data["faculty"], data["subjects"], data["theory"], data["labs"]
    )
    return data


def print_dry_run(data):
    print("Dry-run summary")
    print(f"faculty rows to insert: {len(data['faculty'])}")
    print(f"subject rows to insert: {len(data['subjects'])}")
    print(f"theory allocation rows to insert: {len(data['theory'])}")
    print(f"lab allocation rows to insert: {len(data['labs'])}")
    print("duplicate rows detected: " + ", ".join(
        f"{name}={_duplicate_count(data[key])}"
        for name, key in (("faculty", "faculty"), ("subjects", "subjects"),
                          ("theory", "theory"), ("labs", "labs"))
    ))
    print("rows with missing optional values: " + ", ".join(
        f"{name}={_missing_optional(data[key], fields)}"
        for name, key, fields in (
            ("faculty", "faculty", ("email", "contact", "cabin_no")),
            ("subjects", "subjects", ("subject_name", "regulation", "program", "department", "semester", "category", "course_type", "credits", "hours_per_week", "LTPC")),
            ("theory", "theory", ("batch", "section", "slot", "building_name", "room_number")),
            ("labs", "labs", ("batch", "section", "lab_slot", "building", "room_no", "cofaculty_id")),
        )
    ))
    print(f"rows that would fail validation: {len(data['errors'])}")
    unresolved = [error for error in data["errors"] if "unresolved" in error]
    print(f"unresolved faculty references: {sum('faculty' in error for error in unresolved)}")
    print(f"unresolved subject references: {sum('subject' in error for error in unresolved)}")
    for error in data["errors"]:
        print(f"ERROR: {error}")


def persist_import(data):
    from models.faculty import Faculty
    from models.subject import Subject
    from models.faculty_allocation import FacultyAllocation
    from models.lab_allocation import LabAllocation

    inserted = {"faculty": 0, "subjects": 0, "theory": 0, "labs": 0}
    try:
        for row in data["faculty"]:
            if db.session.get(Faculty, row["faculty_id"]):
                continue
            db.session.add(Faculty(
                faculty_id=row["faculty_id"], username=row["faculty_name"],
                email=row["email"], contact=row["contact"], cabin_no=row["cabin_no"],
                professor_post=row["professor_post"], special_role=row["special_role"],
                role="faculty", password_hash=None,
            ))
            inserted["faculty"] += 1
        db.session.flush()

        for row in data["subjects"]:
            if db.session.get(Subject, row["subject_code"]):
                continue
            db.session.add(Subject(**row))
            inserted["subjects"] += 1
        db.session.flush()
        subjects = {subject.subject_code: subject for subject in Subject.query.all()}

        for row in data["theory"]:
            db.session.add(FacultyAllocation(
                faculty_id=row["faculty_id"], subject_code=row["subject_code"],
                subject_name=subjects[row["subject_code"]].subject_name,
                batch=int(row["batch"]) if row["batch"] else None,
                section=row["section"], slot=row["slot"],
                building_name=row["building_name"], room_number=row["room_number"],
                class_type="theory",
            ))
            inserted["theory"] += 1

        for row in data["labs"]:
            db.session.add(LabAllocation(**row))
            inserted["labs"] += 1
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return inserted


def main():
    parser = argparse.ArgumentParser(description="Import the CSV master data transactionally.")
    parser.add_argument("--import", dest="write", action="store_true", help="Persist after a clean dry-run.")
    args = parser.parse_args()
    data = load_import_data()
    print_dry_run(data)
    if data["errors"]:
        raise SystemExit("Import stopped: validation errors must be fixed first.")
    if not args.write:
        print("No data written. Re-run with --import to persist this clean import.")
        return

    from app import app
    with app.app_context():
        inserted = persist_import(data)
        print("Rows inserted: " + ", ".join(f"{key}={value}" for key, value in inserted.items()))


if __name__ == "__main__":
    main()