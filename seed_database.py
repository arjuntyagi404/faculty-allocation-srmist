from app import app
from config import db

from models.faculty import Faculty
from models.faculty_allocation import FacultyAllocation

from werkzeug.security import generate_password_hash


with app.app_context():

    db.drop_all()
    db.create_all()

    print("Database recreated.")


    admin = Faculty(

    faculty_id="ADMIN",

    username="System Administrator",

    email="admin@srmist.edu",

    contact="0000000000",

    password_hash=generate_password_hash("admin123"),

    role="admin"

    )

    db.session.add(admin)
    db.session.commit()

    print("Admin created.")