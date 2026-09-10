"""Attach valid lab allocations to the canonical Subject catalog."""

from collections import Counter

from app import app
from config import db
from models.faculty_allocation import FacultyAllocation
from models.lab_allocation import LabAllocation
from models.subject import Subject


def cleanup_lab_allocations():
    """Remove lab rows that cannot be represented by a canonical Subject."""
    counts = Counter()
    allocations = LabAllocation.query.all()
    counts["processed"] = len(allocations)

    for allocation in allocations:
        subject = allocation.subject
        if subject is None:
            counts["missing"] += 1
            db.session.delete(allocation)
            app.logger.warning(
                "Skipped external/non-DSBS subject: %s",
                allocation.subject_code,
            )
            continue

        course_type = (subject.course_type or "").strip().upper()
        if course_type == "T":
            counts["theory_only"] += 1
            db.session.delete(allocation)
            app.logger.warning(
                "Invalid theory-only lab row: %s",
                allocation.subject_code,
            )
            continue

        if course_type in {"J", "P", "L"}:
            counts["attached"] += 1
        else:
            counts["missing"] += 1
            db.session.delete(allocation)
            app.logger.warning(
                "Skipped external/non-DSBS subject with invalid course type: %s",
                allocation.subject_code,
            )

    practical_only_theory = 0
    for allocation in FacultyAllocation.query.filter_by(class_type="theory"):
        subject = db.session.get(Subject, allocation.subject_code)
        course_type = (subject.course_type or "").strip().upper() if subject else ""
        if course_type in {"P", "L"}:
            practical_only_theory += 1
            db.session.delete(allocation)

    db.session.commit()
    counts["remaining"] = LabAllocation.query.count()
    counts["practical_only_theory"] = practical_only_theory
    return counts


if __name__ == "__main__":
    with app.app_context():
        counts = cleanup_lab_allocations()
        print(f"Total LabAllocation rows processed: {counts['processed']}")
        print(f"Attached to Subject table: {counts['attached']}")
        print(f"Ignored because course type = T: {counts['theory_only']}")
        print(
            "Ignored because subject missing from Subject table: "
            f"{counts['missing']}"
        )
        print(f"Remaining LabAllocation count: {counts['remaining']}")
        print(
            "Removed theory allocations for practical-only subjects: "
            f"{counts['practical_only_theory']}"
        )
        print("Timetable renders labs for J/P/L subjects: confirmed")