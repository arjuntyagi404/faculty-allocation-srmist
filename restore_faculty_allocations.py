"""Restore one faculty's allocations from the original CSV exports.

This command is deliberately opt-in: pass --apply and --data-dir together.
It never recreates tables or touches rows for another faculty.
"""

import argparse
import csv
from collections import Counter
from pathlib import Path

from app import app
from config import db
from models.faculty_allocation import FacultyAllocation
from models.faculty import Faculty
from models.lab_allocation import LabAllocation

FACULTY_ID = "103140"


def _read_rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def _value(row, *names):
    headers = {str(key).strip().casefold(): key for key in row}
    for name in names:
        key = headers.get(name.casefold())
        if key is not None:
            value = row[key]
            return value.strip() if value is not None else None
    return None


def _batch(value):
    return int(value) if value not in (None, "") else None


def _theory_db_values(row):
    return (
        FACULTY_ID,
        _value(row, "subject_code", "subject code", "code"),
        _value(row, "subject name", "subject_name", "name") or "",
        _value(row, "slot", "theory slot"),
        "theory",
        _batch(_value(row, "batch")),
        _value(row, "section", "sections"),
        _value(row, "room_number", "room number", "room", "room_no"),
        _value(row, "building_name", "building name", "building"),
    )


def _lab_db_values(row):
    return (
        _value(row, "main_faculty_id", "main faculty id"),
        _value(row, "cofaculty_id", "cofaculty id"),
        _value(row, "subject_code", "subject code", "code"),
        _value(row, "batch"),
        _value(row, "section", "sections"),
        _value(row, "lab_slot", "lab slot", "slot"),
        _value(row, "building", "building name", "building_name"),
        _value(row, "room_no", "room number", "room", "room_number"),
    )


def load_source_rows(data_dir):
    theory = [
        row for row in _read_rows(data_dir / "Theory_Allocations.csv")
        if _value(row, "faculty_id", "faculty id", "faculty code") == FACULTY_ID
    ]
    labs = [
        row for row in _read_rows(data_dir / "Lab_Allocations.csv")
        if FACULTY_ID in {
            _value(row, "main_faculty_id", "main faculty id"),
            _value(row, "cofaculty_id", "cofaculty id"),
        }
    ]
    return theory, labs


def restore(data_dir, apply=False):
    theory_rows, lab_rows = load_source_rows(data_dir)
    print(f"Source rows: theory={len(theory_rows)}, labs={len(lab_rows)}")
    if not apply:
        print("Dry run only. Re-run with --apply to change the existing database.")
        return

    with app.app_context():
        faculty = db.session.get(Faculty, FACULTY_ID)
        if faculty is None:
            raise RuntimeError(f"Faculty {FACULTY_ID} does not exist")

        FacultyAllocation.query.filter_by(faculty_id=FACULTY_ID).delete()
        LabAllocation.query.filter(
            db.or_(
                LabAllocation.main_faculty_id == FACULTY_ID,
                LabAllocation.cofaculty_id == FACULTY_ID,
            )
        ).delete(synchronize_session=False)

        for row in theory_rows:
            db.session.add(FacultyAllocation(
                faculty_id=FACULTY_ID,
                subject_code=_value(row, "subject_code", "subject code", "code"),
                subject_name=_value(row, "subject_name", "subject name", "name") or "",
                batch=_batch(_value(row, "batch")),
                section=_value(row, "section", "sections"),
                slot=_value(row, "slot", "theory slot"),
                building_name=_value(row, "building_name", "building name", "building"),
                room_number=_value(row, "room_number", "room number", "room", "room_no"),
                class_type="theory",
            ))
        for row in lab_rows:
            db.session.add(LabAllocation(
                main_faculty_id=_value(row, "main_faculty_id", "main faculty id"),
                cofaculty_id=_value(row, "cofaculty_id", "cofaculty id"),
                subject_code=_value(row, "subject_code", "subject code", "code"),
                batch=_value(row, "batch"),
                section=_value(row, "section", "sections"),
                lab_slot=_value(row, "lab_slot", "lab slot", "slot"),
                building=_value(row, "building", "building name", "building_name"),
                room_no=_value(row, "room_no", "room number", "room", "room_number"),
            ))
        db.session.commit()

        theory_db_rows = [
            (
                allocation.faculty_id,
                allocation.subject_code,
                allocation.subject_name,
                allocation.slot,
                allocation.class_type,
                allocation.batch,
                allocation.section,
                allocation.room_number,
                allocation.building_name,
            )
            for allocation in FacultyAllocation.query.filter_by(
                faculty_id=FACULTY_ID
            ).all()
        ]
        lab_db_rows = [
            (
                allocation.main_faculty_id,
                allocation.cofaculty_id,
                allocation.subject_code,
                allocation.batch,
                allocation.section,
                allocation.lab_slot,
                allocation.building,
                allocation.room_no,
            )
            for allocation in LabAllocation.query.filter(
                db.or_(
                    LabAllocation.main_faculty_id == FACULTY_ID,
                    LabAllocation.cofaculty_id == FACULTY_ID,
                )
            ).all()
        ]
        theory_match = Counter(theory_db_rows) == Counter(
            _theory_db_values(row) for row in theory_rows
        )
        lab_match = Counter(lab_db_rows) == Counter(
            _lab_db_values(row) for row in lab_rows
        )
        subject_codes = [
            _value(row, "subject_code", "subject code", "code")
            for row in theory_rows + lab_rows
        ]
        print(f"Theory allocations restored: {len(theory_rows)}")
        print(f"Lab allocations restored: {len(lab_rows)}")
        print(f"Subject codes restored: {subject_codes}")
        print(
            "Database rows exactly match CSV rows: "
            f"theory={theory_match}, labs={lab_match}"
        )
        if not theory_match or not lab_match:
            raise RuntimeError("Restored database rows do not match CSV rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    restore(args.data_dir, args.apply)
