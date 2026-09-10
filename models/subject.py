from config import db


class Subject(db.Model):
    __tablename__ = "subjects"

    subject_code = db.Column(db.String(30), primary_key=True)
    subject_name = db.Column(db.String(255), nullable=True)
    regulation = db.Column(db.String(20), nullable=True)
    program = db.Column(db.String(50), nullable=True)
    department = db.Column(db.String(150), nullable=True)
    semester = db.Column(db.String(20), nullable=True)
    semester_type = db.Column(db.String(20), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    course_type = db.Column(db.String(20), nullable=True)
    credits = db.Column(db.String(20), nullable=True)
    hours_per_week = db.Column(db.String(20), nullable=True)
    LTPC = db.Column(db.String(50), nullable=True)
    slot = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            "subject_code": self.subject_code,
            "subject_name": self.subject_name,
            "regulation": self.regulation,
            "program": self.program,
            "department": self.department,
            "semester": self.semester,
            "semester_type": self.semester_type,
            "category": self.category,
            "course_type": self.course_type,
            "credits": self.credits,
            "hours_per_week": self.hours_per_week,
            "LTPC": self.LTPC,
            "slot": self.slot,
        }