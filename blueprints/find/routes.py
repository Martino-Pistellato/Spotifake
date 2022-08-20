from flask import Blueprint, render_template
from flask import current_app as app

# Blueprint Configuration
find_bp = Blueprint(
    'find_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@find_bp.route('/find')
def find():
    return render_template("find.html")