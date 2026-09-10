from functools import wraps
from flask import session, redirect
from config import db
from models.faculty import Faculty


def admin_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        admin_id = session.get("admin_id")
        admin = db.session.get(Faculty, admin_id) if admin_id else None
        if admin is None or admin.role != "admin":
            session.pop("admin_id", None)
            session.pop("admin", None)
            return redirect("/admin/login")

        return view(*args, **kwargs)

    return wrapped


def faculty_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        faculty_id = session.get("faculty_id")
        faculty = db.session.get(Faculty, faculty_id) if faculty_id else None
        if faculty is None or faculty.role == "admin":
            session.pop("faculty_id", None)
            return redirect("/faculty/login")

        return view(*args, **kwargs)

    return wrapped