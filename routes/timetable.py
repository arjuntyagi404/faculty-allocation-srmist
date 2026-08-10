from flask import Blueprint, render_template, session, redirect

from models.faculty import Faculty

from scheduler.database_loader import load_allocations
from scheduler.scheduler import generate_schedule
from scheduler.timetable_builder import build_matrix_timetable

timetable_bp = Blueprint(
    "timetable",
    __name__
)


@timetable_bp.route("/timetable")
def timetable():

    faculty_id = session.get("faculty_id")

    if faculty_id is None:
        return redirect("/faculty/login")

    faculty = Faculty.query.get(faculty_id)

    allocation_data = load_allocations(faculty_id)

    if not allocation_data:

        return render_template(
            "timetable.html",
            faculty=faculty,
            timetable=None,
            workload=0
        )

    result = generate_schedule(allocation_data)

    matrix = build_matrix_timetable(
        result["schedule"]
    )

    return render_template(
        "timetable.html",
        faculty=faculty,
        timetable=matrix,
        workload=result["workload"]
    )