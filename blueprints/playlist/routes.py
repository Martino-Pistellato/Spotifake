from flask import Blueprint, render_template, redirect, url_for, request
from flask import current_app as app
from flask_login import *
from blueprints.models import *

# Blueprint Configuration
playlist_bp = Blueprint(
    'playlist_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@playlist_bp.route('/playlist')
@login_required
def playlist():
    return render_template("playlist.html", user=current_user)

@playlist_bp.route('/create_playlist/<string:email>', methods=['GET', 'POST'])
@login_required
def create_playlist(email):
    if request.method == 'POST':
        user = session.query(Users).filter(Users.Email == email).first()
        user.playlists.append(Playlists(Name = request.form["name"]))
        session.commit()
        return redirect(url_for("playlist_bp.show_songs"))

@playlist_bp.route('/show_songs', methods=['GET', 'POST'])
@login_required
def show_songs():
    #sub_stmt1= session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)
    #sub_stmt = session.query(PlaylistsSongs.song_id).filter(Playlists.Id.in_(sub_stmt1))
    #songs = session.query(Songs.Name, Songs.artist, Songs.albums, Songs.Duration).filter(Songs.Id.not_in(sub_stmt))
   
    songs = session.query(Songs).filter(Songs.Id.notin_(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id.not_in(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email == current_user.Email)))))
    return render_template("add_songs.html", songs = songs, user=current_user)

#@playlist_bp.route('/add_songs', methods=['GET', 'POST'])
#@login_required
#def add_songs():
