from flask import Blueprint, render_template, request, redirect, session
from models.faculty import Faculty
from werkzeug.security import check_password_hash
from utils.logger import logger

auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route("/")
def home():
    return render_template("login.html")


@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "GET":
        return render_template("admin_login.html")

    faculty_id = request.form["faculty_id"]
    password = request.form["password"]

    faculty = Faculty.query.get(faculty_id)

    if faculty is None:

        return render_template(
            "admin_login.html",
            error="Invalid credentials."
        )

    if faculty.role != "admin":

        return render_template(
            "admin_login.html",
            error="Access denied."
        )

    if not faculty.password_hash or not check_password_hash(
        faculty.password_hash, password
    ):

        return render_template(
            "admin_login.html",
            error="Invalid credentials."
        )

    session["admin"] = True
    logger.info(f"Admin {faculty.faculty_id} logged in.")
    return redirect("/admin")


@auth_bp.route("/faculty/login", methods=["GET", "POST"])
def faculty_login():

    if request.method == "GET":
        return render_template("faculty_login.html")

    faculty_id = request.form["faculty_id"]
    password = request.form["password"]

    faculty = Faculty.query.get(faculty_id)

    if faculty is None:
        return render_template(
            "faculty_login.html",
            error="Invalid Faculty ID or Password."
        )

    if not faculty.password_hash or not check_password_hash(
        faculty.password_hash, password
    ):
        return render_template(
            "faculty_login.html",
            error="Invalid Faculty ID or Password."
        )

    session["faculty_id"] = faculty.faculty_id
    logger.info(
    f"Faculty {faculty.faculty_id} logged in.")
    
    return redirect("/dashboard")

@auth_bp.route("/dashboard")
def dashboard():

    faculty_id = session.get("faculty_id")

    if faculty_id is None:
        return redirect("/faculty/login")

    faculty = Faculty.query.get(faculty_id)

    from scheduler.database_loader import load_allocations
    from scheduler.workload import calculate_workload

    allocations = load_allocations(faculty_id)

    subjects = sorted({
        allocation["subject_name"]
        for allocation in allocations
    })

    workload = calculate_workload(
        allocations,
        faculty.professor_post,
        faculty.special_role
    )

    return render_template(

        "faculty_dashboard.html",

        faculty=faculty,

        subjects=subjects,

        workload=workload

    )
@auth_bp.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect("/admin/login")

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/faculty/login")