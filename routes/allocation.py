

from config import db
from models.faculty import Faculty
from models.faculty_allocation import FacultyAllocation

from flask import Blueprint, request, jsonify, render_template

from scheduler.config.subjects import SUBJECTS
from scheduler.lookup import get_allocation_periods, TIMETABLE

from utils.auth import admin_required
from utils.validators import validate_allocation
from utils.logger import logger
allocation_bp = Blueprint(
    "allocation",
    __name__
)


def get_lab_start_slots():
    """Return each timetable lab session's first P slot once."""

    slots = {}

    for periods in TIMETABLE.values():
        period_numbers = sorted(int(period) for period in periods)

        batch_keys = {
            batch_key
            for period in period_numbers
            for batch_key in periods[str(period)]
        }

        for batch_key in batch_keys:
            practical_periods = [
                period for period in period_numbers
                if periods[str(period)].get(batch_key, "").startswith("P")
            ]

            runs = []
            for period in practical_periods:
                if not runs or period != runs[-1][-1] + 1:
                    runs.append([period])
                else:
                    runs[-1].append(period)

            for run in runs:
                for index in range(0, len(run) - 1, 2):
                    start_period = run[index]
                    end_period = run[index + 1]
                    start = periods[str(start_period)][batch_key]
                    end = periods[str(end_period)][batch_key]
                    slots[start] = {"start": start, "end": end}

    return sorted(
        slots.values(),
        key=lambda slot: int(slot["start"][1:])
    )


@allocation_bp.route("/allocation/lab-slots")
def lab_slots():
    return jsonify(get_lab_start_slots())
def check_allocation_conflict(
    batch,
    slot,
    class_type,
    subject_code=None,
    section=None,
    exclude_id=None
):
    """
    Check whether an allocation overlaps an existing
    allocation for the same batch.
    """

    new_periods = get_allocation_periods(
        slot,
        batch,
        class_type
    )

    if not new_periods:
        return "Unable to determine timetable periods for this allocation."

    new_positions = {
        (
            period["day"],
            period["period"],
            period["batch"]
        )
        for period in new_periods
    }

    query = FacultyAllocation.query.filter_by(
        batch=batch
    )

    if exclude_id is not None:
        query = query.filter(
            FacultyAllocation.id != exclude_id
        )

    existing_allocations = query.all()

    matching_lab_count = 0

    for existing in existing_allocations:

        existing_periods = get_allocation_periods(
            existing.slot,
            existing.batch,
            existing.class_type
        )

        overlaps = any(
            (
                period["day"],
                period["period"],
                period["batch"]
            ) in new_positions
            for period in existing_periods
        )

        if overlaps:

            same_lab_session = (
                class_type == "practical"
                and existing.class_type == "practical"
                and existing.subject_code == subject_code
                and existing.slot == slot
                and existing.section == section
            )

            if same_lab_session:
                matching_lab_count += 1
                if matching_lab_count >= 2:
                    return (
                        "Maximum of two faculty members can be "
                        "assigned to this lab."
                    )
                continue

            return (
                "Can't do that. There's already a subject "
                "assigned to this slot."
            )

    return None

@allocation_bp.route("/allocation")
@admin_required
def allocation_page():

    return render_template("allocation.html")


@allocation_bp.route("/allocation/add", methods=["POST"])
@admin_required
def add_allocation():

    data = request.get_json()

    error = validate_allocation(data)

    if error:
        return jsonify({
            "error": error
        }), 400

    faculty = Faculty.query.get(data["faculty_id"])

    if faculty is None:
        return jsonify({
            "error": "Faculty not found"
        }), 404

    subject = SUBJECTS.get(data["subject_code"])

    if subject is None:
        return jsonify({
            "error": "Invalid subject code."
        }), 400

    course_type = data["subject_code"][-1]

    # Determine theory/practical
    if course_type == "T":

        class_type = "theory"
        slot = subject["slot"]

    elif course_type == "P":

        class_type = "practical"
        slot = data.get("lab_slot")

    elif course_type == "J":

        class_type = data.get("class_type")

        if class_type not in ["theory", "practical"]:
            return jsonify({
                "error": "Please select Theory or Practical for a J course."
            }), 400

        if class_type == "theory":

            slot = subject["slot"]

        else:
            slot = data.get("lab_slot")

    else:

        return jsonify({
            "error": "Invalid course type."
        }), 400

    valid_lab_slots = {
        lab_slot["start"]
        for lab_slot in get_lab_start_slots()
    }

    if class_type == "practical" and slot not in valid_lab_slots:
        return jsonify({
            "error": "Please select a valid two-period lab session."
        }), 400

    if (
        faculty.professor_post.strip().lower() == "cofaculty"
        and class_type == "theory"
    ):
        return jsonify({
            "error": "Cofaculty can only be assigned to practical/lab classes."
        }), 400

    # Existing duplicate check
    existing = FacultyAllocation.query.filter_by(
        faculty_id=data["faculty_id"],
        subject_code=data["subject_code"],
        batch=data["batch"],
        class_type=class_type
    ).first()

    if existing:

        return jsonify({
            "error": "Allocation already exists."
        }), 400

    # Check physical timetable overlap
    conflict = check_allocation_conflict(
        batch=data["batch"],
        slot=slot,
        class_type=class_type,
        subject_code=data["subject_code"],
        section=data.get("section")
    )

    if conflict:

        return jsonify({
            "error": conflict
        }), 400

    allocation = FacultyAllocation(

        faculty_id=data["faculty_id"],

        subject_code=data["subject_code"],

        subject_name=subject["name"],

        slot=slot,

        class_type=class_type,

        batch=data["batch"],

        section=data.get("section")
        ,
        room_number=data.get("room_number"),
        building_name=data.get("building_name")

    )

    db.session.add(allocation)

    db.session.commit()

    from scheduler.database_loader import load_allocations
    from scheduler.workload import calculate_workload

    workload = calculate_workload(
        load_allocations(allocation.faculty_id),
        faculty.professor_post,
        faculty.special_role
    )

    response = {
        "message": "Allocation added successfully"
    }

    if workload["is_overloaded"]:
        response["warning"] = (
            "Warning: This allocation exceeds the recommended weekly "
            f"workload by {workload['excess_workload']} hours."
        )

    logger.info(
        f"Allocation added: "
        f"{allocation.faculty_id} "
        f"{allocation.subject_code} "
        f"{allocation.class_type} "
        f"Batch {allocation.batch}"
    )

    return jsonify(response), 201

@allocation_bp.route("/allocation/list")
def allocation_list():

    allocations = FacultyAllocation.query.all()

    return jsonify([

        allocation.to_dict()

        for allocation in allocations

    ])

@allocation_bp.route("/allocation/delete/<int:id>", methods=["DELETE"])
@admin_required
def delete_allocation(id):

    allocation = FacultyAllocation.query.get(id)

    if allocation is None:

        return jsonify({
            "error": "Allocation not found."
        }), 404

    db.session.delete(allocation)

    db.session.commit()

    logger.info(
    f"Allocation deleted: {allocation.id}")

    return jsonify({
        "message": "Allocation deleted."
    })

@allocation_bp.route("/allocation/edit/<int:id>", methods=["PUT"])
@admin_required
def edit_allocation(id):

    allocation = FacultyAllocation.query.get(id)

    if allocation is None:
        return jsonify({
            "error": "Allocation not found."
        }), 404

    data = request.get_json()

    error = validate_allocation(data)

    if error:
        return jsonify({
            "error": error
        }), 400

    new_batch = data.get(
        "batch",
        allocation.batch
    )

    new_slot = allocation.slot
    if allocation.class_type == "practical":
        new_slot = data.get("lab_slot", allocation.slot)

        valid_lab_slots = {
            lab_slot["start"]
            for lab_slot in get_lab_start_slots()
        }

        if new_slot not in valid_lab_slots:
            return jsonify({
                "error": "Please select a valid two-period lab session."
            }), 400

    # Check whether moving this allocation creates
    # a conflict with another allocation.
    conflict = check_allocation_conflict(
        batch=new_batch,
        slot=new_slot,
        class_type=allocation.class_type,
        subject_code=allocation.subject_code,
        section=data.get("section", allocation.section),
        exclude_id=allocation.id
    )

    if conflict:
        return jsonify({
            "error": conflict
        }), 400

    allocation.batch = new_batch
    allocation.slot = new_slot

    allocation.section = data.get(
        "section",
        allocation.section
    )
    allocation.room_number = data.get(
        "room_number",
        allocation.room_number
    )

    allocation.building_name = data.get(
        "building_name",
        allocation.building_name
    )

    db.session.commit()

    return jsonify({
        "message": "Allocation updated."
    })

@allocation_bp.route("/allocation/<int:id>")
def get_allocation(id):

    allocation = FacultyAllocation.query.get(id)

    if allocation is None:

        return jsonify({
            "error": "Allocation not found."
        }), 404

    return jsonify(
        allocation.to_dict()
    )