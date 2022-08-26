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
    playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))          
    return render_template("playlist.html", user=current_user, playlists=playlists)

@playlist_bp.route('/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    if request.method == 'POST':
        user = session.query(Users).filter(Users.Email == current_user.Email).first()
        playlist = Playlists(request.form["name"])
        Users.add_playlist(user, playlist)
        
        return redirect(url_for("playlist_bp.show_songs_addable", playlist_name=request.form["name"]))

@playlist_bp.route('/show_songs_addable/<playlist_name>', methods=['GET', 'POST'])
@login_required
def show_songs_addable(playlist_name):
    playlists_id =session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)
    pl_id = session.query(Playlists.Id).filter(Playlists.Name == playlist_name, Playlists.Id.in_(playlists_id))
    songs = session.query(Songs).filter(Songs.Id.not_in(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==pl_id)))
    playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))          
    
    return render_template("add_songs.html", songs = songs, user = current_user, playlist = playlist_name, playlists = playlists)

@playlist_bp.route('/show_playlist_content/<playlist_name>', methods=['GET', 'POST'])
@login_required
def show_playlist_content(playlist_name):
    playlists_id =session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)
    pl_id = session.query(Playlists.Id).filter(Playlists.Name == playlist_name, Playlists.Id.in_(playlists_id))
    songs = session.query(Songs).filter(Songs.Id.in_(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==pl_id)))
    
    #songs = session.query(PlaylistsSongs).filter(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==playlist.Id))
    
    playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))          
    
    return render_template("show_playlist_content.html", songs = songs, user = current_user, playlist = playlist_name, playlists = playlists)


@playlist_bp.route('/add_songs/<song_id>/<playlist>', methods=['GET', 'POST'])
@login_required
def add_songs(playlist, song_id):
    song = session.query(Songs).filter(Songs.Id == song_id).first()
    playlist = session.query(Playlists).filter(and_(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)), Playlists.Name == playlist)).first()
    
    Playlists.add_song_to_playlist(playlist, song)
   
    return redirect(url_for("playlist_bp.show_songs_addable", playlist_name=playlist.Name))

