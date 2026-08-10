from dbm import error

from config import db
from models.faculty import Faculty
from models.faculty_allocation import FacultyAllocation
from flask import Blueprint, request, jsonify, render_template
from scheduler.config.subjects import SUBJECTS
from utils.auth import admin_required
from utils.validators import validate_allocation

allocation_bp = Blueprint(
    "allocation",
    __name__
)


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

    existing = FacultyAllocation.query.filter_by(

    faculty_id=data["faculty_id"],

    subject_code=data["subject_code"],

    batch=data["batch"]

    ).first()

    if existing:

        return jsonify({

        "error": "Allocation already exists."

        }   ), 400

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

    allocation = FacultyAllocation(

    faculty_id=data["faculty_id"],

    subject_code=data["subject_code"],

    subject_name=subject["name"],

    slot=subject["slot"],

    batch=data["batch"],

    section=data.get("section")

    )

    db.session.add(allocation)

    db.session.commit()

    logger.info(

    f"Allocation added: "

    f"{allocation.faculty_id} "

    f"{allocation.subject_code} "

    f"Batch {allocation.batch}"

)

    return jsonify({

        "message": "Allocation added successfully"

    }), 201

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

    allocation.batch = data.get(
        "batch",
        allocation.batch
    )

    allocation.section = data.get(
        "section",
        allocation.section
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