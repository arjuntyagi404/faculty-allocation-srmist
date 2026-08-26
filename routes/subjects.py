from flask import Blueprint, jsonify

from models.subject import Subject
from scheduler.config.subjects import SUBJECTS


subjects_bp = Blueprint(
    "subjects",
    __name__
)


@subjects_bp.route("/subjects")
def get_subjects():

    subjects = Subject.query.order_by(Subject.subject_code).all()
    if subjects:
        data = []
        for subject in subjects:
            item = subject.to_dict()
            if item["category"]:
                item["category"] = item["category"].casefold()
            data.append(item)
        return jsonify(data)

    data = []

    for code, info in SUBJECTS.items():
        data.append({
            "subject_code": info["subject_code"],
            "subject_name": info["subject_name"],
            "regulation": info.get("regulation"),
            "program": info.get("program"),
            "department": info.get("department"),
            "semester": info.get("semester"),
            "category": info["category"],
            "course_type": info["course_type"],
            "credits": info.get("credits"),
            "hours_per_week": info.get("hours_per_week"),
            "LTPC": info.get("LTPC"),
            "slot": info.get("slot"),
            "lab_slots": info.get("lab_slots", {})
        })

    return jsonify(data)