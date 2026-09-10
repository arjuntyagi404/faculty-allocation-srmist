from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from config import db
from models.faculty import Faculty
from models.faculty_allocation import FacultyAllocation
from models.lab_allocation import LabAllocation
from werkzeug.security import generate_password_hash
from utils.auth import admin_required
from utils.validators import validate_faculty
from utils.logger import logger
from utils.special_roles import (
    SPECIAL_ROLES as NORMALIZED_SPECIAL_ROLES,
    normalize_submitted_special_roles,
)


registration_bp = Blueprint('registration', __name__)


@registration_bp.before_app_request
def ensure_cabin_column():
    columns = db.session.execute(
        db.text("PRAGMA table_info(faculty)")
    ).fetchall()
    if columns and not any(column[1] == "cabin_no" for column in columns):
        db.session.execute(db.text(
            "ALTER TABLE faculty ADD COLUMN cabin_no VARCHAR(50)"
        ))
        db.session.commit()

SPECIAL_ROLES = set(NORMALIZED_SPECIAL_ROLES)
PROFESSOR_POSTS = {
    "Professor",
    "Professor & Head",
    "Principal Architect",
    "Associate Professor",
    "Assistant Professor",
    "Assistant Professor - Jr.G",
    "Research Assistant Professor",
    "Teaching Associate",
    "Research Scholar",
}


def validate_special_role(value):
    try:
        return normalize_submitted_special_roles(value)
    except ValueError as error:
        return str(error)

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

    special_role = validate_special_role(data.get("special_role"))
    if special_role == "Invalid special role.":
        return jsonify({"error": special_role}), 400
    if data.get("professor_post", "Assistant Professor") not in PROFESSOR_POSTS:
        return jsonify({"error": "Invalid professor post."}), 400

    new_faculty = Faculty(

    faculty_id=data["faculty_id"],

    username=data["username"],

    email=data["email"],

    contact=data["contact"],

    cabin_no=data.get("cabin_no") or None,

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
    faculty.cabin_no = data.get('cabin_no', faculty.cabin_no)
    professor_post = data.get('professor_post', faculty.professor_post)
    if professor_post not in PROFESSOR_POSTS:
        return jsonify({"error": "Invalid professor post."}), 400
    faculty.professor_post = professor_post
    if "special_role" in data:
        special_role = validate_special_role(data.get("special_role"))
        if special_role == "Invalid special role.":
            return jsonify({"error": special_role}), 400
        faculty.special_role = special_role
    db.session.commit()
    logger.info(
    f"Faculty {faculty.faculty_id} updated.")
    return jsonify({"message": "Faculty updated successfully"})


@registration_bp.route('/faculty/reset-password/<faculty_id>', methods=['POST'])
@admin_required
def reset_faculty_password(faculty_id):
    if faculty_id == session.get("admin_id"):
        return jsonify({"error": "Administrators cannot reset their own password here."}), 403
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404
    data = request.get_json() or {}
    password = data.get("password", "")
    if not isinstance(password, str) or not password:
        return jsonify({"error": "password is required."}), 400
    faculty.password_hash = generate_password_hash(password)
    db.session.commit()
    return jsonify({"message": "Faculty password reset successfully"})


@registration_bp.route('/faculty/register', methods=['GET', 'POST'])
def faculty_register():
    if request.method == 'GET':
        return render_template('register_faculty.html')

    data = request.form
    faculty_id = data.get('faculty_id', '').strip()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    contact = data.get('contact', '').strip()
    cabin_no = data.get('cabin_no', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    error = next((message for condition, message in (
        (not faculty_id or not username or not email or not contact,
         'Faculty ID, full name, email, and phone number are required.'),
        (not cabin_no, 'Cabin number is required.'),
        (password != confirm_password, 'Password and confirm password must match.'),
        (not password, 'Password is required.'),
    ) if condition), None)
    if error:
        return render_template('register_faculty.html', error=error, form=data), 400

    if Faculty.query.get(faculty_id):
        return render_template('register_faculty.html', error='Faculty ID already exists.', form=data), 400
    if Faculty.query.filter_by(email=email).first():
        return render_template('register_faculty.html', error='Email already exists.', form=data), 400

    faculty = Faculty(
        faculty_id=faculty_id,
        username=username,
        email=email,
        contact=contact,
        cabin_no=cabin_no,
        password_hash=generate_password_hash(password),
        role='faculty',
        professor_post='Assistant Professor',
        special_role='None'
    )
    db.session.add(faculty)
    db.session.commit()
    return redirect(url_for('auth.faculty_login', registered='1'))

# REMOVE a faculty
@registration_bp.route('/faculty/remove/<faculty_id>', methods=['DELETE'])
@admin_required
def remove_faculty(faculty_id):
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404

    theory_count = FacultyAllocation.query.filter_by(
        faculty_id=faculty_id
    ).count()
    lab_count = sum(
        faculty_id in {allocation.main_faculty_id, allocation.cofaculty_id}
        for allocation in LabAllocation.query.all()
    )
    required_removals = []
    if theory_count:
        required_removals.append(
            f"{theory_count} theory allocation"
            f"{'s' if theory_count != 1 else ''}"
        )
    if lab_count:
        required_removals.append(
            f"{lab_count} lab allocation"
            f"{'s' if lab_count != 1 else ''}"
        )
    if required_removals:
        return jsonify({
            "error": "Cannot delete faculty. Remove "
            + " and ".join(required_removals)
            + " first."
        }), 409

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
    if not data or not data.get("faculty_id") or not data.get("password"):
        return jsonify({"error": "faculty_id and password are required."}), 400
    from routes.auth import authenticate_faculty
    faculty = authenticate_faculty(data["faculty_id"], data["password"])
    if not faculty:
        return jsonify({"error": "Invalid credentials"}), 401
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