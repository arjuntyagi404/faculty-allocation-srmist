from flask import Blueprint, render_template
from models.faculty import Faculty
from scheduler.database_loader import load_all_allocations
from scheduler.scheduler import generate_schedule
from scheduler.timetable_builder import build_matrix_timetable
from scheduler.workload import calculate_workload
from scheduler.config.period_times import PERIOD_TIMES
from utils.auth import admin_required

admin_bp = Blueprint(
    "admin",
    __name__
)

@admin_bp.route("/admin")
@admin_required
def admin_dashboard():

    return render_template("index.html")


@admin_bp.route("/admin/report")
@admin_required
def faculty_report():

    faculties = Faculty.query.filter(
        Faculty.role != "admin"
    ).order_by(
        Faculty.username
    ).all()
    allocations_by_faculty = load_all_allocations()
    reports = []
    filter_options = {
        "subjects": {},
        "days": set(),
        "times": set(),
        "buildings": set(),
        "rooms": set(),
        "batches": set(),
        "posts": set(),
    }

    for faculty in faculties:
        allocations = allocations_by_faculty.get(
            faculty.faculty_id,
            []
        )

        if allocations:
            result = generate_schedule(
                allocations,
                faculty.professor_post,
                faculty.special_role
            )
        else:
            result = {
                "schedule": [],
                "workload": calculate_workload(
                    [],
                    faculty.professor_post,
                    faculty.special_role
                )
            }

        allocation_times = {}
        for entry in result["schedule"]:
            key = (
                entry["subject_code"],
                entry["class_type"],
                entry["batch"]
            )
            allocation_times.setdefault(key, []).append(entry["time"])

        for allocation in allocations:
            key = (
                allocation["subject_code"],
                allocation["class_type"],
                allocation["batch"]
            )
            allocation["times"] = list(dict.fromkeys(
                allocation_times.get(key, [])
            ))

            filter_options["subjects"][allocation["subject_code"]] = (
                allocation["subject_name"]
            )
            if allocation.get("building_name"):
                filter_options["buildings"].add(
                    allocation["building_name"]
                )
            if allocation.get("room_number"):
                filter_options["rooms"].add(allocation["room_number"])
            filter_options["batches"].add(str(allocation["batch"]))

        for entry in result["schedule"]:
            filter_options["days"].add(entry["day"])
            filter_options["times"].add(entry["time"])

        filter_options["posts"].add(faculty.professor_post)

        reports.append({
            "faculty": faculty,
            "allocations": allocations,
            "workload": result["workload"],
            "timetable": build_matrix_timetable(result["schedule"]),
            "period_times": PERIOD_TIMES,
            "filter_data": {
                "faculty": f"{faculty.username} {faculty.faculty_id}".lower(),
                "subjects": " ".join(
                    f"{allocation['subject_code']} {allocation['subject_name']}"
                    for allocation in allocations
                ).lower(),
                "days": " ".join(
                    entry["day"] for entry in result["schedule"]
                ).lower(),
                "times": " ".join(
                    entry["time"] for entry in result["schedule"]
                ).lower(),
                "buildings": " ".join(
                    allocation.get("building_name") or ""
                    for allocation in allocations
                ).lower(),
                "rooms": " ".join(
                    allocation.get("room_number") or ""
                    for allocation in allocations
                ).lower(),
                "batches": " ".join(
                    str(allocation["batch"]) for allocation in allocations
                ).lower(),
                "post": faculty.professor_post.lower(),
                "special_role": (faculty.special_role or "None").lower(),
            },
        })

    return render_template(
        "faculty_report.html",
        reports=reports,
        filter_options={
            "subjects": sorted(filter_options["subjects"].items()),
            "days": sorted(filter_options["days"]),
            "times": sorted(filter_options["times"]),
            "buildings": sorted(filter_options["buildings"]),
            "rooms": sorted(filter_options["rooms"]),
            "batches": sorted(filter_options["batches"]),
            "posts": sorted(filter_options["posts"]),
            "special_roles": sorted({
                (faculty.special_role or "None")
                for faculty in faculties
            }),
        }
    )