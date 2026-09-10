from flask import Blueprint, render_template, request
from models.faculty import Faculty
from models.subject import Subject
from models.subject_preference import SubjectPreference
from scheduler.database_loader import load_all_allocations
from scheduler.scheduler import generate_schedule
from scheduler.timetable_builder import build_matrix_timetable
from scheduler.workload import calculate_allocation_workload, calculate_workload
from scheduler.config.period_times import PERIOD_TIMES
from utils.conflicts import find_imported_conflicts
from utils.formatting import format_venue
from utils.auth import admin_required
from utils.special_roles import special_role_list

admin_bp = Blueprint(
    "admin",
    __name__
)


def _report_faculty_context():
    faculties = Faculty.query.filter(
        Faculty.role != "admin"
    ).order_by(
        Faculty.username
    ).all()
    faculty_id = request.args.get("faculty_id", "")
    faculty = next(
        (item for item in faculties if item.faculty_id == faculty_id),
        None
    )
    allocations = load_all_allocations().get(faculty_id, []) if faculty else []
    result = generate_schedule(
        allocations,
        faculty.professor_post,
        faculty.special_role
    ) if faculty and allocations else {
        "schedule": [],
        "unscheduled": [],
        "workload": calculate_workload(
            [],
            faculty.professor_post if faculty else None,
            faculty.special_role if faculty else None
        )
    }
    return faculties, faculty, allocations, result

@admin_bp.route("/admin")
@admin_required
def admin_dashboard():

    return render_template("index.html")


@admin_bp.route("/admin/faculty-query")
@admin_required
def faculty_query_portal():

    faculties = Faculty.query.filter(
        Faculty.role != "admin"
    ).order_by(
        Faculty.username
    ).all()
    allocations_by_faculty = load_all_allocations()
    query_rows = []

    for faculty in faculties:
        allocations = allocations_by_faculty.get(
            faculty.faculty_id,
            []
        )
        allocation_lookup = {
            (
                allocation["subject_code"],
                allocation["class_type"],
                allocation["batch"]
            ): allocation
            for allocation in allocations
        }
        schedule = generate_schedule(
            allocations,
            faculty.professor_post,
            faculty.special_role
        )["schedule"] if allocations else []

        for entry in schedule:
            allocation = allocation_lookup.get(
                (
                    entry["subject_code"],
                    entry["class_type"],
                    entry["batch"]
                ),
                {}
            )
            query_rows.append({
                "day": entry["day"],
                "day_order": entry["day"].split()[-1],
                "time": entry["time"],
                "faculty_name": entry["faculty_name"],
                "faculty_id": faculty.faculty_id,
                "professor_post": faculty.professor_post,
                "cabin_no": faculty.cabin_no or "",
                "subject_code": entry["subject_code"],
                "subject_name": entry["subject_name"],
                "building": allocation.get("building_name") or "",
                "room": allocation.get("room_number") or "",
                "venue": format_venue(
                    allocation.get("building_name"),
                    allocation.get("room_number")
                ),
            })

    return render_template(
        "faculty_query.html",
        query_rows=query_rows,
        period_times=PERIOD_TIMES,
        buildings=["TP1", "TP2", "UB", "Main Block", "Biotech", "I-MAC Lab"]
    )


@admin_bp.route("/admin/subject-preference-report")
@admin_required
def subject_preference_report():

    faculties = Faculty.query.filter(
        Faculty.role != "admin"
    ).order_by(
        Faculty.username
    ).all()
    preferences = {
        preference.faculty_id: preference
        for preference in SubjectPreference.query.filter(
            SubjectPreference.faculty_id.in_(
                [faculty.faculty_id for faculty in faculties]
            )
        ).all()
    } if faculties else {}
    subject_names = {
        subject.subject_code: subject.subject_name
        for subject in Subject.query.all()
    }

    return render_template(
        "subject_preference_report.html",
        faculties=faculties,
        preferences=preferences,
        subject_names=subject_names,
        filter_options={
            "posts": sorted({
                faculty.professor_post
                for faculty in faculties
            }),
            "regulations": sorted({
                preference.regulation
                for preference in preferences.values()
                if preference.regulation
            }),
            "programs": sorted({
                preference.program
                for preference in preferences.values()
                if preference.program
            }),
            "semesters": sorted({
                preference.semester_type
                for preference in preferences.values()
                if preference.semester_type
            }),
        }
    )


@admin_bp.route("/admin/report")
@admin_required
def faculty_report():
    return render_template("faculty_report_landing.html")


@admin_bp.route("/admin/report/full")
@admin_required
def faculty_full_report():

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
                "unscheduled": [],
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
            allocation["venue"] = format_venue(
                allocation.get("building_name"),
                allocation.get("room_number")
            )
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
            "unscheduled": result["unscheduled"],
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
                role
                for faculty in faculties
                for role in (special_role_list(faculty.special_role) or ["None"])
            }),
        }
    )


@admin_bp.route("/admin/report/workload")
@admin_required
def workload_report():
    faculties, faculty, allocations, result = _report_faculty_context()
    workload_rows = [
        {
            "subject_code": allocation["subject_code"],
            "subject_name": allocation["subject_name"],
            "hours": calculate_allocation_workload(allocation),
        }
        for allocation in allocations
    ]
    return render_template(
        "workload_report.html",
        faculties=faculties,
        faculty=faculty,
        workload=result["workload"],
        workload_rows=workload_rows,
    )


@admin_bp.route("/admin/report/subject-allocation")
@admin_required
def subject_allocation_report():
    faculties, faculty, allocations, result = _report_faculty_context()
    schedule_by_allocation = {}
    for entry in result["schedule"]:
        key = (entry["subject_code"], entry["class_type"], entry["batch"])
        schedule_by_allocation.setdefault(key, []).append(
            f"{entry['day']} / Period {entry['period']}"
        )
    allocation_rows = []
    for allocation in allocations:
        key = (
            allocation["subject_code"],
            allocation["class_type"],
            allocation["batch"],
        )
        allocation_rows.append({
            **allocation,
            "course_type": allocation.get("course_type") or "",
            "day_slot": ", ".join(dict.fromkeys(schedule_by_allocation.get(key, []))) or "Not scheduled",
            "venue": format_venue(
                allocation.get("building_name"),
                allocation.get("room_number")
            ),
        })
    return render_template(
        "subject_allocation_report.html",
        faculties=faculties,
        faculty=faculty,
        allocations=allocation_rows,
    )


@admin_bp.route("/admin/report/lookup-timetable")
@admin_required
def lookup_timetable_report():
    faculties, faculty, allocations, result = _report_faculty_context()
    timetable = build_matrix_timetable(result["schedule"])
    return render_template(
        "lookup_timetable_report.html",
        faculties=faculties,
        faculty=faculty,
        timetable=timetable if allocations else None,
        period_times=PERIOD_TIMES,
        unscheduled=result["unscheduled"],
    )


@admin_bp.route("/admin/report/conflicts")
@admin_required
def conflict_report():
    return render_template(
        "conflict_report.html",
        conflicts=find_imported_conflicts(),
    )