from models.faculty_allocation import FacultyAllocation


def _allocation_to_dict(allocation):
    return {
        "faculty_id": allocation.faculty_id,
        "faculty_name": allocation.faculty.username,
        "subject_code": allocation.subject_code,
        "subject_name": allocation.subject_name,
        "slot": allocation.slot,
        "class_type": allocation.class_type,
        "batch": allocation.batch,
        "section": allocation.section,
        "room_number": allocation.room_number,
        "building_name": allocation.building_name,
    }


def load_allocations(faculty_id):

    allocations = FacultyAllocation.query.filter_by(
        faculty_id=faculty_id
    ).all()

    result = []

    for allocation in allocations:

        result.append(_allocation_to_dict(allocation))

    return result


def load_all_allocations():
    """Load all allocations once, grouped by faculty ID."""

    result = {}

    for allocation in FacultyAllocation.query.all():
        result.setdefault(allocation.faculty_id, []).append(
            _allocation_to_dict(allocation)
        )

    return result