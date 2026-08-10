from config import db


class FacultyAllocation(db.Model):
    __tablename__ = "faculty_allocations"

    id = db.Column(db.Integer, primary_key=True)

    faculty_id = db.Column(
        db.String(20),
        db.ForeignKey("faculty.faculty_id"),
        nullable=False
    )

    subject_code = db.Column(db.String(20), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)

    slot = db.Column(db.String(2), nullable=False)

    batch = db.Column(db.Integer, nullable=False)

    # We'll use this later
    section = db.Column(db.String(20), nullable=True)

    def to_dict(self):

        return {

            "id": self.id,

            "faculty_id": self.faculty_id,

            "faculty_name": self.faculty.username,

            "subject_code": self.subject_code,

            "subject_name": self.subject_name,

            "slot": self.slot,

            "batch": self.batch,

            "section": self.section

        }
