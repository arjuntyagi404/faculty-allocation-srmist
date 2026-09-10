from models.faculty_allocation import FacultyAllocation
from models.faculty import Faculty
from models.lab_allocation import LabAllocation
from models.subject import Subject


def _allocation_to_dict(allocation, subjects):
    subject = subjects.get(allocation.subject_code)
    return {
        "faculty_id": allocation.faculty_id,
        "faculty_name": allocation.faculty.username,
        "subject_code": allocation.subject_code,
        "subject_name": subject.subject_name if subject else "",
        "slot": subject.slot if subject else None,
        "class_type": allocation.class_type,
        "batch": allocation.batch,
        "section": allocation.section,
        "room_number": allocation.room_number,
        "building_name": allocation.building_name,
    }


def _lab_allocation_to_dict(allocation):
    subject = allocation.subject
    return {
        "faculty_id": allocation.main_faculty_id,
        "faculty_name": "",
        "subject_code": allocation.subject_code,
        "subject_name": subject.subject_name if subject else "",
        "slot": allocation.lab_slot,
        "class_type": "practical",
        "course_type": subject.course_type if subject else None,
        "batch": allocation.batch,
        "section": allocation.section,
        "room_number": allocation.room_no,
        "building_name": allocation.building,
    }


def _load_lab_allocations():
    faculty_names = {
        faculty.faculty_id: faculty.username
        for faculty in Faculty.query.all()
    }
    subjects = {subject.subject_code: subject for subject in Subject.query.all()}
    result = {}
    for allocation in LabAllocation.query.all():
        subject = allocation.subject
        course_type = (subject.course_type or "").strip().upper() if subject else ""
        if subject is None or course_type == "T":
            continue
        lab = _lab_allocation_to_dict(allocation)
        lab["faculty_name"] = faculty_names.get(allocation.main_faculty_id, "")
        result.setdefault(allocation.main_faculty_id, []).append(lab)
        if allocation.cofaculty_id:
            co_lab = {**lab, "faculty_id": allocation.cofaculty_id}
            co_lab["faculty_name"] = faculty_names.get(
                allocation.cofaculty_id,
                ""
            )
            result.setdefault(allocation.cofaculty_id, []).append(co_lab)
    return result


def load_allocations(faculty_id):

    allocations = FacultyAllocation.query.filter_by(
        faculty_id=faculty_id
    ).all()

    subjects = {subject.subject_code: subject for subject in Subject.query.all()}
    result = []

    for allocation in allocations:

        result.append(_allocation_to_dict(allocation, subjects))

    result.extend(_load_lab_allocations().get(faculty_id, []))

    return result


def load_all_allocations():
    """Load all allocations once, grouped by faculty ID."""

    subjects = {subject.subject_code: subject for subject in Subject.query.all()}
    result = {}

    for allocation in FacultyAllocation.query.all():
        result.setdefault(allocation.faculty_id, []).append(
            _allocation_to_dict(allocation, subjects)
        )

    for faculty_id, allocations in _load_lab_allocations().items():
        result.setdefault(faculty_id, []).extend(allocations)

    return result