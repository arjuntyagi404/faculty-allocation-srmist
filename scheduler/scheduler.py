from scheduler.lookup import get_allocation_periods
from scheduler.config.period_times import PERIOD_TIMES


def generate_schedule(
    faculty_allocations,
    professor_post=None,
    special_role=None
):
    """
    Generates a complete timetable for one faculty.
    """

    timetable = []

    for allocation in faculty_allocations:

        slot = allocation["slot"]
        batch = allocation["batch"]
        class_type = allocation.get("class_type", "theory")

        occurrences = get_allocation_periods(
            slot,
            batch,
            class_type
        )

        for occurrence in occurrences:

            timetable.append(
                {
                    "faculty_id": allocation["faculty_id"],
                    "faculty_name": allocation["faculty_name"],

                    "subject_code": allocation["subject_code"],
                    "subject_name": allocation["subject_name"],

                    "slot": slot,
                    "class_type": class_type,
                    "batch": batch,

                    "day": occurrence["day"],
                    "period": occurrence["period"],
                    "time": PERIOD_TIMES[occurrence["period"]]
                }
            )

    timetable.sort(
        key=lambda x: (
            int(x["day"].split()[-1]),
            x["period"]
        )
    )

    from scheduler.workload import calculate_workload

    return {
        "faculty_id": faculty_allocations[0]["faculty_id"],
        "faculty_name": faculty_allocations[0]["faculty_name"],
        "schedule": timetable,
        "workload": calculate_workload(
            faculty_allocations,
            professor_post,
            special_role
        )
    }