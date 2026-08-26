from config import db


class LabAllocation(db.Model):
    __tablename__ = "lab_allocations"

    id = db.Column(db.Integer, primary_key=True)
    main_faculty_id = db.Column(db.String(20), nullable=False)
    cofaculty_id = db.Column(db.String(20), nullable=True)
    subject_code = db.Column(db.String(30), nullable=True)
    batch = db.Column(db.String(50), nullable=True)
    section = db.Column(db.String(50), nullable=True)
    lab_slot = db.Column(db.String(255), nullable=True)
    building = db.Column(db.String(100), nullable=True)
    room_no = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "main_faculty_id": self.main_faculty_id,
            "cofaculty_id": self.cofaculty_id,
            "subject_code": self.subject_code,
            "batch": self.batch,
            "section": self.section,
            "lab_slot": self.lab_slot,
            "building": self.building,
            "room_no": self.room_no,
        }