from scheduler.lookup import lookup_slot


def generate_schedule(faculty_allocations):
    """
    Generates a complete timetable for one faculty.

    Parameters
    ----------
    faculty_allocations : list[dict]

    Returns
    -------
    list[dict]
    """

    timetable = []

    for allocation in faculty_allocations:

        slot = allocation["slot"]
        batch = allocation["batch"]

        occurrences = lookup_slot(slot, batch)

        for occurrence in occurrences:

            timetable.append(
                {
                    "faculty_id": allocation["faculty_id"],
                    "faculty_name": allocation["faculty_name"],

                    "subject_code": allocation["subject_code"],
                    "subject_name": allocation["subject_name"],

                    "slot": slot,
                    "batch": batch,

                    "day": occurrence["day"],
                    "period": occurrence["period"]
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
    "workload": calculate_workload(timetable)
    }   


if __name__ == "__main__":

    from scheduler.sample_data import faculty_allocations

    faculty = generate_schedule(faculty_allocations)

    from pprint import pprint

    pprint(faculty)