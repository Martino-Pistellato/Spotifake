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
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    
        return render_template("upload_song.html", user = current_user, playlists = playlists)

@song_bp.route('/create_song', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def create_song():
    if (current_user.Profile == 'Artist'):
        if request.method == 'POST':
            name = request.form["name"]
            duration = request.form["duration"]
            genre = request.form["genre"]
            restriction = request.form["restriction"]
            if (name is not None and duration is not None and genre is not None and restriction is not None):
                rest = restriction == "Sì"
                song = Songs(name, duration, genre, rest, current_user.Email)
                Songs.create_song(song)
                user = session.query(Users).filter(Users.Email == current_user.Email).first()
                Users.add_song_if_artist(user, song)
                
                return redirect(url_for("song_bp.show_my_songs"))

@song_bp.route('/show_my_songs')
@login_required # richiede autenticazione
def show_my_songs():
    if (current_user.Profile == 'Artist'):
        songs = session.query(Songs).filter(Songs.Artist == current_user.Email)
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    
        return render_template("show_my_songs.html", songs = songs, user = current_user, playlists = playlists)

@song_bp.route('/edit_songs/<song_id>')
@login_required # richiede autenticazione
def edit_songs(song_id):
    if (current_user.Profile == 'Artist'):
        song = session.query(Songs).filter(Songs.Id == song_id).first()
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        
        return render_template("edit_song.html", user=current_user, playlists=playlists, name=song.Name, duration=song.Duration, genre=song.Genre, id=song_id, restriction=song.Is_Restricted)

@song_bp.route('/update_songs/<song_id>/<restr>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def update_songs(song_id, restr):
    if (current_user.Profile == 'Artist'):
        if request.method == 'POST':
            name = request.form["name"]
            duration = request.form["duration"]
            genre = request.form["genre"]
            restriction = request.form["restriction"]
            if (name is not None and duration is not None and genre is not None):
                if(restriction is not None):
                    restr = not restr
                Songs.update_song(song_id, name, duration, genre, restr)
                
                return redirect(url_for("song_bp.show_my_songs"))

@song_bp.route('/delete_songs/<int:song_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def delete_songs(song_id):
    if (current_user.Profile == 'Artist'):
        Songs.delete_song(song_id)
        
        return redirect(url_for("song_bp.show_my_songs"))