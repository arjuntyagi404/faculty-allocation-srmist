import re

from scheduler.config_loader import load_unified_timetable

TIMETABLE = load_unified_timetable()


def lookup_slot(slot: str, batch: int):
    """
    Find every occurrence of a theory slot for a given batch.

    Example:
        A + batch 1 -> A1
        B + batch 2 -> B2
    """

    target = f"{slot}{batch}"
    batch_key = f"batch{batch}"

    results = []

    for day, periods in TIMETABLE.items():

        for period, values in periods.items():

            if values.get(batch_key) == target:

                results.append({
                    "day": day,
                    "period": int(period),
                    "cell": target
                })

    return results


def lookup_practical_slot(slot: str):
    """
    Find an exact practical slot such as P1, P2, P3, etc.

    Practical slots are already uniquely identified in
    the unified timetable, so batch is determined by
    the timetable itself.
    """

    results = []

    for day, periods in TIMETABLE.items():

        for period, values in periods.items():

            for batch_key, cell in values.items():

                if cell == slot:

                    results.append({
                        "day": day,
                        "period": int(period),
                        "batch": int(batch_key[-1]),
                        "cell": cell
                    })

    return results

def get_lab_periods(slot: str):
    """
    Return the two timetable periods occupied by a lab.

    The practical slot itself identifies the first period.
    The following period must belong to the same batch.
    """

    occurrences = lookup_practical_slot(slot)

    if not occurrences:
        return []

    occurrence = occurrences[0]

    day = occurrence["day"]
    first_period = occurrence["period"]
    batch = occurrence["batch"]

    periods = TIMETABLE[day]

    second_period = first_period + 1

    if str(second_period) not in periods:
        return []

    second_values = periods[str(second_period)]
    batch_key = f"batch{batch}"

    first_cell = periods[str(first_period)][batch_key]
    second_cell = second_values[batch_key]

    # Make sure the second period is also a practical slot
    # belonging to the same batch.
    if (
        second_cell.startswith("P")
        and first_cell.startswith("P")
    ):
        return [
            {
                "day": day,
                "period": first_period,
                "batch": batch,
                "cell": first_cell
            },
            {
                "day": day,
                "period": second_period,
                "batch": batch,
                "cell": second_cell
            }
        ]

    return []

def get_allocation_periods(slot: str, batch: int, class_type: str):
    """
    Resolve an allocation into its physical timetable positions.

    Theory:
        A + batch 1 -> all A1 occurrences

    Practical:
        P6 -> P6 + P7
    """

    if class_type == "practical":

        if not slot:
            return []

        range_match = re.search(
            r"P0*(\d+)\s*-\s*P0*(\d+)",
            slot.upper()
        )
        if range_match:
            start_number = int(range_match.group(1))
            end_number = int(range_match.group(2))
            if end_number < start_number:
                return []

            starts = lookup_practical_slot(f"P{start_number}")
            if not starts:
                return []

            first = starts[0]
            periods = TIMETABLE[first["day"]]
            results = []
            for period in range(
                first["period"],
                first["period"] + end_number - start_number + 1
            ):
                values = periods.get(str(period), {})
                cell = values.get(f"batch{first['batch']}", "")
                expected = f"P{start_number + period - first['period']}"
                if cell != expected:
                    return []
                results.append({
                    "day": first["day"],
                    "period": period,
                    "batch": batch
                })
            return results

        occurrences = lookup_practical_slot(slot)

        if not occurrences:
            return []

        # A lab occupies two consecutive periods.
        first = occurrences[0]

        day = first["day"]
        first_period = first["period"]

        periods = TIMETABLE[day]
        second_period = first_period + 1

        if str(second_period) not in periods:
            return []

        timetable_batch_key = f"batch{first['batch']}"

        first_cell = periods[str(first_period)][timetable_batch_key]
        second_cell = periods[str(second_period)][timetable_batch_key]

        if (
            first_cell.startswith("P")
            and second_cell.startswith("P")
        ):
            return [
                {
                    "day": day,
                    "period": first_period,
                    "batch": batch
                },
                {
                    "day": day,
                    "period": second_period,
                    "batch": batch
                }
            ]

        return []

    # Theory
    occurrences = lookup_slot(slot, batch)

    return [
        {
            "day": occurrence["day"],
            "period": occurrence["period"],
            "batch": batch
        }
        for occurrence in occurrences
    ]