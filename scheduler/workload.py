from utils.special_roles import SPECIAL_ROLE_WORKLOAD_ROLES


WORKLOAD_RULES = {
    ("J", "theory"): 3,
    ("J", "practical"): 4,
    ("P", "practical"): 4,
    ("T", "theory"): 3,
}

WORKLOAD_CAPACITIES = {
    "Professor": 18,
    "Professor & Head": 18,
    "Assistant Professor": 16,
    "Assistant Professor - Jr.G": 16,
    "Associate Professor": 14,
}

DEFAULT_WORKLOAD_CAPACITY = 10

SPECIAL_ROLE_WORKLOAD = 2


def calculate_allocation_workload(allocation):
    """Return the weekly workload for one allocation."""

    subject_code = allocation["subject_code"]
    course_type = subject_code[-1].upper()
    class_type = allocation.get("class_type", "theory").lower()

    if allocation.get("non_credit"):
        return 2

    if course_type == "P":
        return 4

    return WORKLOAD_RULES.get((course_type, class_type), 0)


def calculate_workload(allocations, professor_post=None, special_role=None):
    """Return assigned and capacity-based weekly workload details."""

    assigned_workload = sum(
        calculate_allocation_workload(allocation)
        for allocation in allocations
    )
    base_required_workload = WORKLOAD_CAPACITIES.get(
        professor_post,
        DEFAULT_WORKLOAD_CAPACITY,
    )
    role_adjustment = (
        SPECIAL_ROLE_WORKLOAD
        if special_role in SPECIAL_ROLE_WORKLOAD_ROLES
        else 0
    )
    required_workload = base_required_workload + role_adjustment

    if required_workload is None:
        return {
            "assigned_workload": assigned_workload,
            "required_workload": None,
            "pending_workload": None,
            "excess_workload": None,
            "is_overloaded": False,
        }

    pending_workload = max(required_workload - assigned_workload, 0)
    excess_workload = max(assigned_workload - required_workload, 0)

    return {
        "assigned_workload": assigned_workload,
        "required_workload": required_workload,
        "pending_workload": pending_workload,
        "excess_workload": excess_workload,
        "is_overloaded": assigned_workload > required_workload,
    }


if __name__ == "__main__":

    from scheduler.scheduler import generate_schedule
    from scheduler.sample_data import faculty_allocations

    schedule = generate_schedule(faculty_allocations)

    print(schedule["workload"])