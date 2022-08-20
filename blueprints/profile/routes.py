from flask import Blueprint, render_template
from flask import current_app as app


# Blueprint Configuration
profile_bp = Blueprint(
    'profile_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@profile_bp.route('/')
def profile():
    return render_template("profile.html")
