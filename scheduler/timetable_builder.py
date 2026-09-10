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

    # Fill timetable, retaining every event that occupies a period.
    for lecture in schedule:

        day = lecture["day"]
        period = lecture["period"] - 1

        event = {
            "subject_code": lecture["subject_code"],
            "subject": lecture["subject_name"],
            "slot": lecture["slot"],
            "batch": lecture["batch"],
            "section": lecture.get("section"),
            "class_type": lecture.get("class_type", "theory"),
            "venue": lecture.get("venue", "Venue: Unassigned"),
            "time": lecture["time"]
        }
        timetable[day][period] = timetable[day][period] if timetable[day][period] else []
        timetable[day][period].append(event)

    for periods in timetable.values():
        for events in periods:
            if events:
                events.sort(key=lambda event: (
                    0 if event["class_type"] == "theory" else 1,
                    event["subject_code"],
                    str(event["batch"]),
                    str(event["section"] or ""),
                ))

    return timetable

