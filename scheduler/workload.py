def calculate_workload(schedule):
    """
    Calculates the total teaching workload.

    Each scheduled period counts as one teaching hour.
    """

    return len(schedule)


if __name__ == "__main__":

    from scheduler.scheduler import generate_schedule
    from scheduler.sample_data import faculty_allocations

    schedule = generate_schedule(faculty_allocations)

    print(calculate_workload(schedule))