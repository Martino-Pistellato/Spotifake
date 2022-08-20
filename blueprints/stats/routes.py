from flask import Blueprint, render_template
from flask import current_app as app
from flask_login import *

login_manager=LoginManager()
login_manager.init_app(app)

# Blueprint Configuration
stats_bp = Blueprint(
    'stats_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@stats_bp.route('/stats')
@login_required # richiede autenticazione
def home():
    return render_template("stats.html")