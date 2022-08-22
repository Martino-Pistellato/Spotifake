from flask import Blueprint, render_template, redirect, url_for, request
from flask import current_app as app
from flask_login import *
from blueprints.models import *

# Blueprint Configuration
song_bp = Blueprint(
    'song_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@song_bp.route('/upload_song')
@login_required # richiede autenticazione
def upload_song():
    if (current_user.Profile == 'Artist'):
        return render_template("upload_song.html", user = current_user)

@song_bp.route('/create_song', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def create_song():
    if (current_user.Profile == 'Artist'):
        if request.method == 'POST':
            name = request.form["name"]
            duration = request.form["duration"]
            genre = request.form["genre"]
            if (name is not None and duration is not None and genre is not None):
                song = Songs(name, duration, genre)
                Songs.create_song(song)
                user = session.query(Users).filter(Users.Email == current_user.Email).first()
                Users.add_song_if_artist(user, song)
                return render_template("upload_song.html", user = current_user)

#@song_bp.route('/show_my_songs')
#@login_required # richiede autenticazione
#def show_my_songs():
#    if (current_user.Profile == 'Artist'):