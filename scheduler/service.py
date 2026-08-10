from scheduler.database_loader import load_allocations
from scheduler.scheduler import generate_schedule


def generate_faculty_schedule(faculty_id):

    allocations = load_allocations(faculty_id)

    if not allocations:
        return None

    return generate_schedule(allocations)