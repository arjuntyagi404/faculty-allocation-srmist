from config import db

class Faculty(db.Model):
    __tablename__ = "faculty"

    faculty_id = db.Column(db.String(20), primary_key=True)

    username = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    contact = db.Column(
        db.String(15),
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="faculty"
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

            "role": self.role

        }