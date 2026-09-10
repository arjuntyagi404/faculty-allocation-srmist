from flask import Blueprint, render_template, session, redirect

from models.faculty import Faculty

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/dashboard")
def dashboard():

    faculty_id = session.get("faculty_id")

    if faculty_id is None:
        return redirect("/faculty/login")

    faculty = Faculty.query.get(faculty_id)
    if faculty is None:
        session.pop("faculty_id", None)
        return redirect("/faculty/login")

    return render_template(
        "dashboard.html",
        faculty=faculty
    )