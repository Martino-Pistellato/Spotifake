from flask import Blueprint, render_template, redirect, url_for
from flask import current_app as app
from flask_login import *
from blueprints import *

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
    playlists = session.query(Playlists.Name).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))          
    return render_template("home.html", user=current_user, playlists=playlists)