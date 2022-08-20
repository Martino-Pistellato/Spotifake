from flask import Blueprint, render_template
from flask import current_app as app


# Blueprint Configuration
album_bp = Blueprint(
    'album_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@album_bp.route('/album')
def album():
    render_template("album.html")