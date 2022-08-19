from flask import Blueprint, render_template
from flask import current_app as app


# Blueprint Configuration
login_bp = Blueprint(
    'login_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@login_bp.route('/')
def login():
    return render_template("login.html")