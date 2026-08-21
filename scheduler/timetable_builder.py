def build_matrix_timetable(schedule):
    """
    Converts the flat schedule list into a timetable matrix.

    Returns

    {
        "Day 1": [cell1, cell2, ...],
        "Day 2": [...],
        ...
    }
    """

    timetable = {}

    # Create empty timetable
    for day in range(1, 6):
        timetable[f"Day {day}"] = [""] * 10

    # Fill timetable
    for lecture in schedule:

        day = lecture["day"]
        period = lecture["period"] - 1

        timetable[day][period] = {
            "subject": lecture["subject_name"],
            "slot": lecture["slot"],
            "batch": lecture["batch"],
            "time": lecture["time"]
        }

    return timetable

if __name__ == "__main__":

    from scheduler.scheduler import generate_schedule
    from scheduler.sample_data import faculty_allocations

    faculty = generate_schedule(faculty_allocations)

    matrix = build_matrix_timetable(
    faculty["schedule"]
    )


    print()

    print("Faculty:", faculty["faculty_name"])

    print("Workload:", faculty["workload"])

    print()

    from pprint import pprint

    pprint(matrix)