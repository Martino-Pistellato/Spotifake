from flask import Blueprint, render_template, redirect, url_for, request
from flask import current_app as app
from flask_login import *
from blueprints.models import *

# Blueprint Configuration
stats_bp = Blueprint(
    'stats_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@stats_bp.route('/stats')
def stats():
    playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))
    return render_template("stats.html", user=current_user, playlists=playlists)