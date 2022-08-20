from flask import Blueprint, render_template, redirect, url_for
from flask import current_app as app
from flask_login import *

login_manager=LoginManager()
login_manager.init_app(app)

# Blueprint Configuration
profile_bp = Blueprint(
    'profile_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@profile_bp.route('/profile')
@login_required # richiede autenticazione
def profile():
    return render_template("profile.html", user = current_user)
