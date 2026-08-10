from scheduler.config_loader import load_unified_timetable

TIMETABLE = load_unified_timetable()


def lookup_slot(slot: str, batch: int):
    """
    Find every occurrence of a slot for a given batch.
    """

    target = f"{slot}{batch}"

    batch_key = f"batch{batch}"

    results = []

    for day, periods in TIMETABLE.items():

        for period, values in periods.items():

            if values[batch_key] == target:

                results.append(
                    {
                        "day": day,
                        "period": int(period),
                        "cell": target
                    }
                )

    return results


if __name__ == "__main__":

    print(lookup_slot("A", 1))