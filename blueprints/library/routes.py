from flask import Blueprint, render_template
from flask import current_app as app

# Blueprint Configuration
library_bp = Blueprint(
    'library_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@library_bp.route('/library')
def library():
    return render_template("library.html")