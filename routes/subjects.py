from flask import Blueprint, jsonify

from scheduler.config.subjects import SUBJECTS


subjects_bp = Blueprint(
    "subjects",
    __name__
)


@subjects_bp.route("/subjects")
def get_subjects():

    data = []

    for code, info in SUBJECTS.items():

        course_type = code[-1]

        data.append({

            "subject_code": code,

            "subject_name": info["name"],

            "slot": info["slot"],

            "course_type": course_type,

            "lab_slots": info.get("lab_slots", {})

        })

    return jsonify(data)