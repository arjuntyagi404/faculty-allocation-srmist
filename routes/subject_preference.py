from flask import Blueprint, redirect, render_template, request, session

from config import db
from models.faculty import Faculty
from models.subject_preference import SubjectPreference
from models.subject import Subject


subject_preference_bp = Blueprint(
    "subject_preference",
    __name__
)

PREFERENCE_FIELDS = (
    "regulation",
    "program",
    "semester_type",
    "core_preference_1",
    "core_preference_2",
    "core_preference_3",
    "elective_preference_1",
    "elective_preference_2",
    "elective_preference_3",
)

FA_SEMESTERS = tuple(f"Semester {number}" for number in range(1, 9))

FA_SUBJECT_CODES = {
    "Semester 1": ("26CSE1001J",),
    "Semester 2": ("21CSC101T",),
    "Semester 3": (
        "21CSC201J",
        "21CSC202J",
        "21CSS201T",
        "21CSS202T",
        "21CSC203P",
        "21CSC206P",
    ),
    "Semester 4": ("21CSC204J", "21CSC205P", "21CSC206T"),
    "Semester 5": (
        "21CSC301T",
        "21CSC302J",
        "21CSC307P",
        "21CSC305T",
        "21CSC307T",
    ),
    "Semester 6": ("21CSC303J", "21CSC304J", "21CSS301T", "21CSS303T"),
    "Semester 7": ("21GNH401T",),
    "Semester 8": (),
}

EXPERIENCE_FIELDS = tuple(
    f"{group}_{field}_{number}"
    for group in ("core", "elective")
    for field in (
        "times_handled",
        "teaching_hours",
        "has_ecurricula",
        "has_online_lectures",
    )
    for number in (1, 2, 3)
)

CURRICULA = {
    "UG": (
        ("Computer Science and Business Systems", "https://webstor.srmist.edu.in/web_assets/downloads/2026/computer-science-and-business-system-curriculum-2021.pdf", "https://webstor.srmist.edu.in/web_assets/downloads/2026/btech-csbs-syllabus-2021.pdf"),
        ("Computer Science Engineering (Data Science)", "https://webstor.srmist.edu.in/web_assets/downloads/2026/cse-data-science-curriculum-2021.pdf", "https://webstor.srmist.edu.in/web_assets/downloads/2026/computing-programmes-syllabus-2021.pdf"),
        ("Computer Science Engineering (Big Data Analytics)", "https://webstor.srmist.edu.in/web_assets/downloads/2026/cse-with-spl-in-big-data-analytics.pdf", "https://webstor.srmist.edu.in/web_assets/downloads/2026/computing-programmes-syllabus-2021.pdf"),
        ("Computer Science Engineering (Blockchain Technology)", "https://webstor.srmist.edu.in/web_assets/downloads/2026/cse-with-spl-in-blockchain-technology-curriculum-2021.pdf", "https://webstor.srmist.edu.in/web_assets/downloads/2026/computing-programmes-syllabus-2021.pdf"),
        ("Computer Science Engineering (Gaming Technology)", "https://webstor.srmist.edu.in/web_assets/downloads/2026/cse-with-spl-in-gaming-technology-curriculum-2021.pdf", "https://webstor.srmist.edu.in/web_assets/downloads/2026/computing-programmes-syllabus-2021.pdf"),
    ),
    "PG": (
        ("Integrated M.Tech CSE (Data Science)", "https://webstor.srmist.edu.in/web_assets/downloads/2026/integrated-mtech-in-cse-with-spl-in-data-science-curriculum-2021.pdf", "https://webstor.srmist.edu.in/web_assets/downloads/2026/computing-programmes-syllabus-2021.pdf"),
    ),
}


def _faculty_context():
    faculty_id = session.get("faculty_id")
    if faculty_id is None:
        return None, redirect("/faculty/login")

    faculty = Faculty.query.get(faculty_id)
    if faculty is None:
        session.pop("faculty_id", None)
        return None, redirect("/faculty/login")

    return faculty, None


def _fa_core_subjects():
    subject_codes = {
        code
        for codes in FA_SUBJECT_CODES.values()
        for code in codes
    }
    subjects = Subject.query.filter(
        Subject.subject_code.in_(subject_codes),
        db.func.lower(Subject.category) == "core",
    ).order_by(Subject.subject_code).all()
    subjects_by_code = {
        subject.subject_code: {
            "code": subject.subject_code,
            "name": subject.subject_name,
        }
        for subject in subjects
        if (subject.category or "").casefold() == "core"
    }
    return {
        semester: [subjects_by_code[code] for code in codes if code in subjects_by_code]
        for semester in FA_SEMESTERS
        for codes in [FA_SUBJECT_CODES[semester]]
    }


def _subjects_by_category():
    subjects = Subject.query.order_by(Subject.subject_code).all()
    return {
        category: [
            {"code": subject.subject_code, "name": subject.subject_name}
            for subject in subjects
            if (subject.category or "").casefold() == category
        ]
        for category in ("core", "elective", "lab")
    }


@subject_preference_bp.route("/subject-preference")
def view_subject_preference():
    faculty, response = _faculty_context()
    if response:
        return response

    preference = SubjectPreference.query.filter_by(
        faculty_id=faculty.faculty_id
    ).first()
    subjects_by_category = _subjects_by_category()
    fa_core_subjects = _fa_core_subjects()

    return render_template(
        "subject_preference.html",
        faculty=faculty,
        preference=preference,
        subjects_by_category=subjects_by_category,
        curricula=CURRICULA,
        fa_semesters=FA_SEMESTERS,
        fa_core_subjects=fa_core_subjects,
        form_error=None,
        form_values={}
    )


@subject_preference_bp.route("/subject-preference/submit", methods=["POST"])
def submit_subject_preference():
    faculty, response = _faculty_context()
    if response:
        return response

    regulation = request.form.get("regulation", "").strip()
    program = request.form.get("program", "").strip()
    department = request.form.get("department", "").strip()
    fa_semester = request.form.get("fa_semester", "").strip()
    fa_error = None
    if "FA" in faculty.special_role.split(","):
        fa_core_subjects = _fa_core_subjects()
        allowed_fa_codes = {
            subject["code"] for subject in fa_core_subjects.get(fa_semester, [])
        }
        if fa_semester not in FA_SEMESTERS:
            fa_error = "Select the semester for which you are FA."
        elif allowed_fa_codes and request.form.get("core_preference_1", "") not in allowed_fa_codes:
            fa_error = "Select a configured FA subject as Core Preference 1 for the chosen semester."
    numeric_fields = (
        field for field in EXPERIENCE_FIELDS
        if field.endswith("times_handled_1")
        or field.endswith("times_handled_2")
        or field.endswith("times_handled_3")
        or field.endswith("teaching_hours_1")
        or field.endswith("teaching_hours_2")
        or field.endswith("teaching_hours_3")
    )
    numeric_values = {}
    numeric_error = None
    for field in numeric_fields:
        raw_value = request.form.get(field, "").strip()
        if not raw_value:
            numeric_values[field] = None
            continue
        try:
            numeric_value = int(raw_value)
        except ValueError:
            numeric_error = "Experience values must be whole numbers."
            break
        if numeric_value < 0:
            numeric_error = "Times handled and teaching hours cannot be negative."
            break
        numeric_values[field] = numeric_value
    if not regulation or not program or not department:
        preference = SubjectPreference.query.filter_by(
            faculty_id=faculty.faculty_id
        ).first()
        subjects_by_category = _subjects_by_category()
        return render_template(
            "subject_preference.html",
            faculty=faculty,
            preference=preference,
            subjects_by_category=subjects_by_category,
            curricula=CURRICULA,
            fa_semesters=FA_SEMESTERS,
            fa_core_subjects=_fa_core_subjects(),
            form_error=fa_error or "Select a regulation, program, and department before saving.",
            form_values=request.form
        ), 400

    if numeric_error or fa_error:
        preference = SubjectPreference.query.filter_by(
            faculty_id=faculty.faculty_id
        ).first()
        subjects_by_category = _subjects_by_category()
        return render_template(
            "subject_preference.html",
            faculty=faculty,
            preference=preference,
            subjects_by_category=subjects_by_category,
            curricula=CURRICULA,
            fa_semesters=FA_SEMESTERS,
            fa_core_subjects=_fa_core_subjects(),
            form_error=numeric_error or fa_error,
            form_values=request.form
        ), 400

    if regulation != "2021":
        return redirect("/subject-preference")

    preference = SubjectPreference.query.filter_by(
        faculty_id=faculty.faculty_id
    ).first()
    if preference is None:
        preference = SubjectPreference(faculty_id=faculty.faculty_id)
        db.session.add(preference)

    for field in PREFERENCE_FIELDS:
        if field in request.form:
            setattr(preference, field, request.form.get(field))

    preference.regulation = regulation
    preference.program = program
    preference.department = department
    if "FA" in faculty.special_role.split(","):
        preference.fa_semester = fa_semester
    else:
        preference.fa_semester = None
    for field, value in numeric_values.items():
        setattr(preference, field, value)
    for field in EXPERIENCE_FIELDS:
        if field.endswith("has_ecurricula_1") or field.endswith("has_ecurricula_2") or field.endswith("has_ecurricula_3"):
            setattr(preference, field, request.form.get(field) == "yes")
        elif field.endswith("has_online_lectures_1") or field.endswith("has_online_lectures_2") or field.endswith("has_online_lectures_3"):
            setattr(preference, field, request.form.get(field) == "yes")

    db.session.commit()
    return redirect("/subject-preference")
