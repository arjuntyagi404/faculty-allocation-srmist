from functools import wraps
from flask import session, redirect


def admin_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if not session.get("admin"):
            return redirect("/admin/login")

        return view(*args, **kwargs)

    return wrapped


def faculty_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if not session.get("faculty_id"):
            return redirect("/faculty/login")

        return view(*args, **kwargs)

    return wrapped