from flask import Blueprint, jsonify

from models.subject import Subject


subjects_bp = Blueprint(
    "subjects",
    __name__
)


@subjects_bp.route("/subjects")
def get_subjects():
    subjects = Subject.query.order_by(Subject.subject_code).all()
    data = []
    for subject in subjects:
        item = subject.to_dict()
        if item["category"]:
            item["category"] = item["category"].casefold()
        data.append(item)
    return jsonify(data)