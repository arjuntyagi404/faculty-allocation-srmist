from models.faculty_allocation import FacultyAllocation


def load_allocations(faculty_id):

    allocations = FacultyAllocation.query.filter_by(
        faculty_id=faculty_id
    ).all()

    result = []

    for allocation in allocations:

        result.append({

            "faculty_id": allocation.faculty_id,

            "faculty_name": allocation.faculty.username,

            "subject_code": allocation.subject_code,

            "subject_name": allocation.subject_name,

            "slot": allocation.slot,

            "batch": allocation.batch

        })

    return result