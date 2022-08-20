from flask import Blueprint, render_template
from flask import current_app as app


# Blueprint Configuration
playlist_bp = Blueprint(
    'playlist_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@playlist_bp.route('/playlist')
def playlist():
    render_template("playlist.html")