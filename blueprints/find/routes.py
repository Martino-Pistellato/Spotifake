from flask import Blueprint, render_template, redirect, url_for
from flask import current_app as app
from flask_login import *
from blueprints import *

# Blueprint Configuration
find_bp = Blueprint(
    'find_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@find_bp.route('/find')
def find():
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    songs = session.query(Songs)
    return render_template("find.html", user = current_user, playlists = playlists, songs=songs)