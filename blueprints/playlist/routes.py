from flask import Blueprint, render_template
from flask import current_app as app


# Blueprint Configuration
playlist_bp = Blueprint(
    'palylist_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

playlist_bp.route('/')
def album_home():
    render_template("playlist.html")