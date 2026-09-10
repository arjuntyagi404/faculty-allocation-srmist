from flask import Blueprint, render_template, session, redirect

from models.faculty import Faculty

from scheduler.database_loader import load_allocations
from scheduler.scheduler import generate_schedule
from scheduler.timetable_builder import build_matrix_timetable
from scheduler.config.period_times import PERIOD_TIMES

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
    if faculty is None:
        session.pop("faculty_id", None)
        return redirect("/faculty/login")

    allocation_data = load_allocations(faculty_id)

    if not allocation_data:

        from scheduler.workload import calculate_workload

        return render_template(
            "timetable.html",
            faculty=faculty,
            timetable=None,
            unscheduled=[],
            workload=calculate_workload(
                [],
                faculty.professor_post,
                faculty.special_role
            ),
            period_times=PERIOD_TIMES
        )

    result = generate_schedule(
        allocation_data,
        faculty.professor_post,
        faculty.special_role
    )

    matrix = build_matrix_timetable(
        result["schedule"]
    )

    return render_template(
        "timetable.html",
        faculty=faculty,
        timetable=matrix,
        unscheduled=result["unscheduled"],
        workload=result["workload"],
        period_times=PERIOD_TIMES
    )