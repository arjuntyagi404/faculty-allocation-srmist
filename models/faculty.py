from config import db


class Faculty(db.Model):
    __tablename__ = "faculty"

    faculty_id = db.Column(
        db.String(20),
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=True
    )

    contact = db.Column(
        db.String(15),
        nullable=True
    )

    cabin_no = db.Column(
        db.String(50),
        nullable=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=True
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="faculty"
    )

    professor_post = db.Column(
        db.String(80),
        nullable=True,
        default="Assistant Professor"
    )

    special_role = db.Column(
        db.String(150),
        nullable=True,
        default="None"
    )

    allocations = db.relationship(
        "FacultyAllocation",
        backref="faculty"
    )

    def to_dict(self):

        return {
            "faculty_id": self.faculty_id,
            "username": self.username,
            "email": self.email,
            "contact": self.contact,
            "cabin_no": self.cabin_no,
            "role": self.role,
            "professor_post": self.professor_post,
            "special_role": self.special_role or "None"
        }