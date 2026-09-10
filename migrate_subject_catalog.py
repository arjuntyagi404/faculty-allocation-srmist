"""Reconcile Subject_Master.csv into the existing subjects table."""

from collections import Counter

from app import app
from config import db
from models.subject import Subject
from seed_database import import_subject_master

FA_SUBJECT_CODES = {
    "Semester 1": ("26CSE1001J",),
    "Semester 2": ("21CSC101T",),
    "Semester 3": (
        "21CSC201J", "21CSC202J", "21CSS201T", "21CSS202T",
        "21CSC203P", "21CSC206P",
    ),
    "Semester 4": ("21CSC204J", "21CSC205P", "21CSC206T"),
    "Semester 5": (
        "21CSC301T", "21CSC302J", "21CSC307P", "21CSC305T", "21CSC307T",
    ),
    "Semester 6": ("21CSC303J", "21CSC304J", "21CSS301T", "21CSS303T"),
    "Semester 7": ("21GNH401T",),
    "Semester 8": (),
}


def reconcile_subjects():
    rows = import_subject_master()
    updated = 0
    inserted = 0
    fields = (
        "subject_name", "regulation", "program", "department", "semester",
        "category", "semester_type", "course_type", "credits",
        "hours_per_week", "LTPC", "slot",
    )
    for row in rows:
        code = row["subject_code"].strip()
        subject = db.session.get(Subject, code)
        if subject is None:
            subject = Subject(subject_code=code)
            db.session.add(subject)
            inserted += 1
        else:
            updated += 1
        for field in fields:
            setattr(subject, field, row.get(field))
    db.session.commit()
    return updated, inserted


def validate():
    subjects = Subject.query.all()
    by_code = {subject.subject_code: subject for subject in subjects}
    duplicate_codes = [
        code for code, count in Counter(subject.subject_code for subject in subjects).items()
        if count > 1
    ]
    missing_slots = sorted(
        subject.subject_code for subject in subjects if not subject.slot
    )
    fa_counts = {
        semester: sum(
            1 for code in codes
            if code in by_code and (by_code[code].category or "").casefold() == "core"
        )
        for semester, codes in FA_SUBJECT_CODES.items()
    }
    allocation_codes = {
        allocation
        for allocation in db.session.execute(
            db.text("SELECT subject_code FROM faculty_allocations")
        ).scalars()
    }
    allocation_codes.update(
        allocation
        for allocation in db.session.execute(
            db.text("SELECT subject_code FROM lab_allocations")
        ).scalars()
    )
    unresolved = sorted(
        code for code in allocation_codes
        if code not in by_code or not by_code[code].slot
    )
    return duplicate_codes, missing_slots, fa_counts, unresolved


if __name__ == "__main__":
    with app.app_context():
        updated, inserted = reconcile_subjects()
        duplicate_codes, missing_slots, fa_counts, unresolved = validate()
        print(f"Subjects updated: {updated}")
        print(f"Subjects inserted: {inserted}")
        print("Duplicate subject codes resolved: " + ", ".join(duplicate_codes or ["None"]))
        print("Subjects still missing slots: " + ", ".join(missing_slots or ["None"]))
        print("FA Semester subject counts:")
        for semester in ("Semester 1", "Semester 2", "Semester 3", "Semester 4",
                         "Semester 5", "Semester 6", "Semester 7", "Semester 8"):
            print(f"  {semester}: {fa_counts[semester]}")
        print("Timetable subjects missing Subject.slot: " + ", ".join(unresolved or ["None"]))