from flask import Blueprint, render_template
from utils.auth import admin_required

admin_bp = Blueprint(
    "admin",
    __name__
)

@admin_bp.route("/admin")
@admin_required
def admin_dashboard():

    return render_template("index.html")