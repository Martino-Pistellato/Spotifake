from flask import Blueprint, render_template
from flask import current_app as app

# Blueprint Configuration
stats_bp = Blueprint(
    'stats_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@stats_bp.route('/stats')
def stats():
    return render_template("stats.html")