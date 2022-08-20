from flask import Blueprint, render_template, redirect, url_for
from flask import current_app as app
from flask_login import *

login_manager=LoginManager()
login_manager.init_app(app)

# Blueprint Configuration
home_bp = Blueprint(
    'home_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@home_bp.route('/home')
@login_required # richiede autenticazione
def home():
    return render_template("home.html", user=current_user)