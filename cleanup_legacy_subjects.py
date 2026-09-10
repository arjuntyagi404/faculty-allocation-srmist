"""Remove unreferenced subjects absent from the final subject master."""

import csv
from pathlib import Path

from app import app
from config import db
from models.faculty_allocation import FacultyAllocation
from models.subject import Subject
from models.subject_preference import SubjectPreference


DATA_DIR = Path(__file__).resolve().parent / "data"
PREFERENCE_FIELDS = (
    "core_preference_1", "core_preference_2", "core_preference_3",
    "elective_preference_1", "elective_preference_2", "elective_preference_3",
)


def official_subject_codes():
    with (DATA_DIR / "Subject_Master.csv").open(
        "r", encoding="utf-8-sig", newline=""
    ) as csv_file:
        return {
            row["subject_code"].strip()
            for row in csv.DictReader(csv_file)
            if row.get("subject_code") and row["subject_code"].strip()
        }


def referenced_subject_codes():
    references = {
        "FacultyAllocation": {
            (allocation.subject_code or "").strip()
            for allocation in FacultyAllocation.query.all()
            if allocation.subject_code
        },
        "SubjectPreference": set(),
    }
    for preference in SubjectPreference.query.all():
        references["SubjectPreference"].update(
            getattr(preference, field).strip()
            for field in PREFERENCE_FIELDS
            if getattr(preference, field)
        )
    return references


def cleanup():
    official_codes = official_subject_codes()
    references = referenced_subject_codes()
    all_references = set().union(*references.values())
    legacy_subjects = [
        subject for subject in Subject.query.all()
        if (subject.subject_code or "").strip() not in official_codes
    ]
    retained = sorted(
        subject.subject_code for subject in legacy_subjects
        if subject.subject_code.strip() in all_references
    )
    deleted = sorted(
        subject.subject_code for subject in legacy_subjects
        if subject.subject_code.strip() not in all_references
    )
    for subject in legacy_subjects:
        if subject.subject_code.strip() not in all_references:
            db.session.delete(subject)
    db.session.commit()
    return deleted, retained, len(Subject.query.all())


if __name__ == "__main__":
    with app.app_context():
        deleted, retained, final_count = cleanup()
        print("Subjects deleted: " + ", ".join(deleted or ["None"]))
        print("Subjects retained because referenced: " + ", ".join(retained or ["None"]))
        print(f"Final subject count: {final_count}")