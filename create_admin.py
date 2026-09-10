import getpass

from app import app
from config import db
from models.faculty import Faculty
from werkzeug.security import generate_password_hash


def create_admin_account(faculty_id, name, email, contact, password):
    if not all((faculty_id, name, email, contact, password)):
        raise ValueError("faculty ID, name, email, contact, and password are required")
    if db.session.get(Faculty, faculty_id):
        raise ValueError("a faculty account with that ID already exists")
    if Faculty.query.filter_by(email=email).first():
        raise ValueError("an account with that email already exists")

    admin = Faculty(
        faculty_id=faculty_id,
        username=name,
        email=email,
        contact=contact,
        password_hash=generate_password_hash(password),
        role="admin",
        professor_post="Assistant Professor",
        special_role="None",
    )
    db.session.add(admin)
    db.session.commit()
    return admin


def main():
    print("Create administrator account")
    faculty_id = input("Faculty ID: ").strip()
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    contact = input("Contact: ").strip()
    password = getpass.getpass("Password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    with app.app_context():
        try:
            admin = create_admin_account(
                faculty_id, name, email, contact, password
            )
        except ValueError as error:
            raise SystemExit(str(error)) from error
    print(f"Administrator created for faculty ID {admin.faculty_id}.")


if __name__ == "__main__":
    main()