import os

from flask import Flask, render_template

from config import db
from schema_migration import migrate_schema
from routes.auth import auth_bp
from routes.registration import registration_bp
from routes.timetable import timetable_bp
from routes.admin import admin_bp
from routes.allocation import allocation_bp
from routes.subjects import subjects_bp
from routes.dashboard import dashboard_bp
from routes.subject_preference import subject_preference_bp
from flask import session, redirect
from utils.auth import admin_required
from utils.special_roles import (
    SPECIAL_ROLES,
    normalize_special_role,
    special_role_list,
)
from models.faculty import Faculty

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///database.db'
)
app.config['SECRET_KEY'] = os.getenv(
    'SECRET_KEY',
    'development-only-change-this-secret'
)

db.init_app(app)

app.register_blueprint(registration_bp)
app.register_blueprint(timetable_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(allocation_bp)
app.register_blueprint(subjects_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(subject_preference_bp)

app.jinja_env.globals.update(
    special_role_options=SPECIAL_ROLES,
    special_role_list=special_role_list,
)

with app.app_context():
    db.create_all()
    migrate_schema(db)

    faculty_columns = db.session.execute(
        db.text("PRAGMA table_info(faculty)")
    ).fetchall()
    if not any(column[1] == "special_role" for column in faculty_columns):
        db.session.execute(db.text(
            "ALTER TABLE faculty ADD COLUMN special_role "
            "VARCHAR(20) NOT NULL DEFAULT 'None'"
        ))
        db.session.commit()

    for faculty in Faculty.query.all():
        normalized_role = normalize_special_role(faculty.special_role)
        if faculty.special_role != normalized_role:
            faculty.special_role = normalized_role
    db.session.commit()

    preference_columns = db.session.execute(
        db.text("PRAGMA table_info(subject_preferences)")
    ).fetchall()
    if preference_columns and not any(
        column[1] == "department" for column in preference_columns
    ):
        db.session.execute(db.text(
            "ALTER TABLE subject_preferences ADD COLUMN department "
            "VARCHAR(150)"
        ))
        db.session.commit()

    preference_columns = db.session.execute(
        db.text("PRAGMA table_info(subject_preferences)")
    ).fetchall()
    preference_column_names = {column[1] for column in preference_columns}
    for column_name, column_type in {
        "fa_semester": "VARCHAR(20)",
    }.items():
        if preference_columns and column_name not in preference_column_names:
            db.session.execute(db.text(
                f"ALTER TABLE subject_preferences ADD COLUMN "
                f"{column_name} {column_type}"
            ))
    if preference_columns:
        db.session.commit()

    experience_columns = {
        "core_times_handled_1": "INTEGER",
        "core_times_handled_2": "INTEGER",
        "core_times_handled_3": "INTEGER",
        "elective_times_handled_1": "INTEGER",
        "elective_times_handled_2": "INTEGER",
        "elective_times_handled_3": "INTEGER",
        "core_teaching_hours_1": "INTEGER",
        "core_teaching_hours_2": "INTEGER",
        "core_teaching_hours_3": "INTEGER",
        "elective_teaching_hours_1": "INTEGER",
        "elective_teaching_hours_2": "INTEGER",
        "elective_teaching_hours_3": "INTEGER",
        "core_has_ecurricula_1": "BOOLEAN",
        "core_has_ecurricula_2": "BOOLEAN",
        "core_has_ecurricula_3": "BOOLEAN",
        "elective_has_ecurricula_1": "BOOLEAN",
        "elective_has_ecurricula_2": "BOOLEAN",
        "elective_has_ecurricula_3": "BOOLEAN",
        "core_has_online_lectures_1": "BOOLEAN",
        "core_has_online_lectures_2": "BOOLEAN",
        "core_has_online_lectures_3": "BOOLEAN",
        "elective_has_online_lectures_1": "BOOLEAN",
        "elective_has_online_lectures_2": "BOOLEAN",
        "elective_has_online_lectures_3": "BOOLEAN",
    }
    existing_columns = {column[1] for column in preference_columns}
    for column_name, column_type in experience_columns.items():
        if preference_columns and column_name not in existing_columns:
            db.session.execute(db.text(
                f"ALTER TABLE subject_preferences ADD COLUMN "
                f"{column_name} {column_type}"
            ))
    if preference_columns:
        db.session.commit()


@app.route('/')
def index():

    return render_template(
        "login.html"
    )

@app.errorhandler(404)
def not_found(error):

    logger.warning("404: Page not found.")

    return render_template(
        "404.html"
    ), 404
@app.errorhandler(500)
def server_error(error):

    logger.exception(error)

    return render_template(
        "500.html"
    ), 500
from utils.logger import logger

if __name__ == "__main__":

    app.run(
        debug=True
    )