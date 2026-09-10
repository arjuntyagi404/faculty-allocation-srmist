from config import db


class SubjectPreference(db.Model):
    __tablename__ = "subject_preferences"

    id = db.Column(db.Integer, primary_key=True)

    faculty_id = db.Column(
        db.String(20),
        db.ForeignKey("faculty.faculty_id"),
        nullable=False,
        unique=True
    )

    regulation = db.Column(db.String(20), nullable=True)
    program = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(150), nullable=True)
    semester_type = db.Column(db.String(20), nullable=True)
    fa_semester = db.Column(db.String(20), nullable=True)
    core_preference_1 = db.Column(db.String(100), nullable=True)
    core_preference_2 = db.Column(db.String(100), nullable=True)
    core_preference_3 = db.Column(db.String(100), nullable=True)
    elective_preference_1 = db.Column(db.String(100), nullable=True)
    elective_preference_2 = db.Column(db.String(100), nullable=True)
    elective_preference_3 = db.Column(db.String(100), nullable=True)

    core_times_handled_1 = db.Column(db.Integer, nullable=True)
    core_times_handled_2 = db.Column(db.Integer, nullable=True)
    core_times_handled_3 = db.Column(db.Integer, nullable=True)
    elective_times_handled_1 = db.Column(db.Integer, nullable=True)
    elective_times_handled_2 = db.Column(db.Integer, nullable=True)
    elective_times_handled_3 = db.Column(db.Integer, nullable=True)

    core_teaching_hours_1 = db.Column(db.Integer, nullable=True)
    core_teaching_hours_2 = db.Column(db.Integer, nullable=True)
    core_teaching_hours_3 = db.Column(db.Integer, nullable=True)
    elective_teaching_hours_1 = db.Column(db.Integer, nullable=True)
    elective_teaching_hours_2 = db.Column(db.Integer, nullable=True)
    elective_teaching_hours_3 = db.Column(db.Integer, nullable=True)

    core_has_ecurricula_1 = db.Column(db.Boolean, nullable=True)
    core_has_ecurricula_2 = db.Column(db.Boolean, nullable=True)
    core_has_ecurricula_3 = db.Column(db.Boolean, nullable=True)
    elective_has_ecurricula_1 = db.Column(db.Boolean, nullable=True)
    elective_has_ecurricula_2 = db.Column(db.Boolean, nullable=True)
    elective_has_ecurricula_3 = db.Column(db.Boolean, nullable=True)

    core_has_online_lectures_1 = db.Column(db.Boolean, nullable=True)
    core_has_online_lectures_2 = db.Column(db.Boolean, nullable=True)
    core_has_online_lectures_3 = db.Column(db.Boolean, nullable=True)
    elective_has_online_lectures_1 = db.Column(db.Boolean, nullable=True)
    elective_has_online_lectures_2 = db.Column(db.Boolean, nullable=True)
    elective_has_online_lectures_3 = db.Column(db.Boolean, nullable=True)
