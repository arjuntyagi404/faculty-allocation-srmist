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

        data.append({

            "subject_code": code,

            "subject_name": info["name"],

            "slot": info["slot"]

        })

    return jsonify(data)