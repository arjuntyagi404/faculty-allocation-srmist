from models.faculty import Faculty
from models.faculty_allocation import FacultyAllocation
from models.lab_allocation import LabAllocation
from models.subject import Subject
from scheduler.lookup import get_allocation_periods


CONFLICT_GROUPS = (
    "Faculty conflicts",
    "Batch/Section conflicts",
    "Room conflicts",
)


def _periods(allocation):
    return {
        (item["day"], item["period"])
        for item in get_allocation_periods(
            allocation["slot"],
            allocation["batch"],
            allocation["class_type"],
        )
    }


def _allocation_rows():
    faculty_names = {
        faculty.faculty_id: faculty.username
        for faculty in Faculty.query.all()
    }
    subject_names = {
        subject.subject_code: subject.subject_name
        for subject in Subject.query.all()
    }
    rows = []

    for allocation in FacultyAllocation.query.all():
        rows.append({
            "key": ("theory", allocation.id),
            "faculty_ids": {allocation.faculty_id},
            "faculty": {faculty_names.get(allocation.faculty_id, allocation.faculty_id)},
            "subject_code": allocation.subject_code,
            "subject_name": allocation.subject_name,
            "batch": str(allocation.batch) if allocation.batch is not None else "",
            "section": allocation.section or "",
            "slot": allocation.slot or "Unassigned",
            "class_type": allocation.class_type,
            "building": allocation.building_name,
            "room": allocation.room_number,
        })

    for allocation in LabAllocation.query.all():
        faculty_ids = {
            allocation.main_faculty_id,
            allocation.cofaculty_id,
        } - {None}
        rows.append({
            "key": ("lab", allocation.id),
            "faculty_ids": faculty_ids,
            "faculty": {
                faculty_names.get(faculty_id, faculty_id)
                for faculty_id in faculty_ids
            },
            "subject_code": allocation.subject_code or "",
            "subject_name": subject_names.get(allocation.subject_code, ""),
            "batch": str(allocation.batch) if allocation.batch is not None else "",
            "section": allocation.section or "",
            "slot": allocation.lab_slot or "Unassigned",
            "class_type": "practical",
            "building": allocation.building,
            "room": allocation.room_no,
        })

    for row in rows:
        row["periods"] = _periods(row)
    return rows


def _same_lab_session(left, right):
    return (
        left["key"][0] == "lab"
        and right["key"][0] == "lab"
        and left["subject_code"] == right["subject_code"]
        and left["slot"] == right["slot"]
        and left["batch"] == right["batch"]
        and left["section"] == right["section"]
    )


def _conflict_row(left, right, reason):
    return {
        "faculty": " / ".join(sorted(left["faculty"] | right["faculty"])),
        "subject": " / ".join(sorted({
            f"{row['subject_code']} — {row['subject_name']}".strip(" —")
            for row in (left, right)
        })),
        "batch": " / ".join(sorted({left["batch"], right["batch"]} - {""})),
        "section": " / ".join(sorted({left["section"], right["section"]} - {""})),
        "slot": " / ".join(sorted({left["slot"], right["slot"]})),
        "reason": reason,
    }


def find_imported_conflicts():
    conflicts = {group: [] for group in CONFLICT_GROUPS}
    rows = _allocation_rows()

    for index, left in enumerate(rows):
        for right in rows[index + 1:]:
            if _same_lab_session(left, right):
                continue
            if not left["periods"] & right["periods"]:
                continue

            if left["faculty_ids"] & right["faculty_ids"]:
                conflicts["Faculty conflicts"].append(_conflict_row(
                    left, right, "Faculty is assigned to overlapping classes."
                ))
            if (
                left["batch"]
                and left["batch"] == right["batch"]
                and left["section"] == right["section"]
            ):
                conflicts["Batch/Section conflicts"].append(_conflict_row(
                    left, right, "Batch and section have overlapping classes."
                ))
            if (
                left["building"]
                and left["room"]
                and left["building"] == right["building"]
                and left["room"] == right["room"]
            ):
                conflicts["Room conflicts"].append(_conflict_row(
                    left, right, "Room is assigned to overlapping classes."
                ))

    for rows_for_group in conflicts.values():
        rows_for_group.sort(key=lambda row: (
            row["slot"], row["faculty"], row["subject"], row["batch"], row["section"]
        ))
    return conflicts
