from flask import Blueprint, request, jsonify
from config import db
from models.faculty import Faculty
from werkzeug.security import generate_password_hash
from utils.auth import admin_required
from utils.validators import validate_faculty
from utils.logger import logger


registration_bp = Blueprint('registration', __name__)

SPECIAL_ROLES = {"None", "FA", "AA", "TC", "FUND"}


def validate_special_role(value):
    if value not in SPECIAL_ROLES:
        return "Invalid special role."
    return None

# ADD a faculty
@registration_bp.route('/faculty/add', methods=['POST'])
@admin_required
def add_faculty():
    data = request.get_json()

    error = validate_faculty(data)

    if error:

        return jsonify({

            "error": error

        }), 400
    if Faculty.query.get(data['faculty_id']):
        return jsonify({"error": "Faculty ID already exists"}), 400

    special_role = data.get("special_role") or "None"
    role_error = validate_special_role(special_role)
    if role_error:
        return jsonify({"error": role_error}), 400

    new_faculty = Faculty(

    faculty_id=data["faculty_id"],

    username=data["username"],

    email=data["email"],

    contact=data["contact"],

    password_hash=generate_password_hash(
        data["password"]
    ),

    role=data.get(
        "role",
        "faculty"
    )

    ,
    professor_post=data.get(
        "professor_post",
        "Assistant Professor"
    ),

    special_role=special_role

    )
    
    db.session.add(new_faculty)
    db.session.commit()
    logger.info(
    f"Faculty {new_faculty.faculty_id} registered.")
    return jsonify({"message": "Faculty added successfully"}), 201

# EDIT a faculty
@registration_bp.route('/faculty/edit/<faculty_id>', methods=['PUT'])
@admin_required
def edit_faculty(faculty_id):
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404

    data = request.get_json()
    error = next(
        (
            f"{field} is required."
            for field in ("username", "email", "contact")
            if not data.get(field)
        ),
        None
    )

    if error:

        return jsonify({

            "error": error

        }), 400
    faculty.username = data.get('username', faculty.username)
    faculty.email    = data.get('email',    faculty.email)
    faculty.contact  = data.get('contact',  faculty.contact)
    faculty.professor_post = data.get('professor_post', faculty.professor_post)
    if "special_role" in data:
        special_role = data.get("special_role") or "None"
        role_error = validate_special_role(special_role)
        if role_error:
            return jsonify({"error": role_error}), 400
        faculty.special_role = special_role
    db.session.commit()
    logger.info(
    f"Faculty {faculty.faculty_id} updated.")
    return jsonify({"message": "Faculty updated successfully"})

# REMOVE a faculty
@registration_bp.route('/faculty/remove/<faculty_id>', methods=['DELETE'])
@admin_required
def remove_faculty(faculty_id):
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404

    db.session.delete(faculty)
    db.session.commit()
    logger.info(
    f"Faculty {faculty.faculty_id} deleted."
)
    return jsonify({"message": "Faculty removed successfully"})

# LOGIN
@registration_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    error = validate_faculty(data)

    if error:

        return jsonify({

            "error": error

        }), 400



    faculty = Faculty.query.get(data['faculty_id'])
    if not faculty:
        return jsonify({"error": "Invalid Faculty ID"}), 401
    return jsonify({"message": "Login successful", "faculty": faculty.to_dict()})
# GET faculty by ID (used by frontend for edit/remove preview)
@registration_bp.route('/faculty/<faculty_id>', methods=['GET'])
def get_faculty(faculty_id):
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404
    return jsonify(faculty.to_dict())

@registration_bp.route("/faculty/list", methods=["GET"])
def faculty_list():

    faculty = Faculty.query.order_by(Faculty.username).all()

    return jsonify([

        {
            "faculty_id": f.faculty_id,
            "username": f.username
        }

        for f in faculty

    ])