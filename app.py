from flask import Flask, render_template

from config import db
from routes.auth import auth_bp
from routes.registration import registration_bp
from routes.timetable import timetable_bp
from routes.admin import admin_bp
from routes.allocation import allocation_bp
from routes.subjects import subjects_bp
from routes.dashboard import dashboard_bp
from flask import session, redirect
from utils.auth import admin_required

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'srmist-secret-key'

db.init_app(app)

app.register_blueprint(registration_bp)
app.register_blueprint(timetable_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(allocation_bp)
app.register_blueprint(subjects_bp)
app.register_blueprint(dashboard_bp)

with app.app_context():
    db.create_all()


@app.route('/')
def index():

    return render_template(
        "login.html"
    )

@app.errorhandler(404)
def not_found(error):

    logger.warning("404: Page not found.")

    return render_template(
        "404.html"
    ), 404
@app.errorhandler(500)
def server_error(error):

    logger.exception(error)

    return render_template(
        "500.html"
    ), 500
from utils.logger import logger

if __name__ == "__main__":

    app.run(
        debug=True
    )