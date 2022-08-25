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
        user.playlists.append(Playlists(request.form["name"]))
        session.commit()
        playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))
        
        return redirect(url_for("playlist_bp.show_songs", playlists=playlists, playlist=request.form["name"]))

@playlist_bp.route('/show_songs/<playlist>', methods=['GET', 'POST'])
@login_required
def show_songs(playlist):
    playlists_id =session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)
    pl_id = session.query(Playlists.Id).filter(Playlists.Name == playlist, Playlists.Id.in_(playlists_id))
    songs = session.query(Songs).filter(Songs.Id.not_in(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==pl_id)))
    playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))          
    
    return render_template("add_songs.html", songs = songs, user=current_user, playlist = playlist, playlists=playlists)

@playlist_bp.route('/show_playlist/<playlist>', methods=['GET', 'POST'])
@login_required
def show_playlist(playlist):
    #playlists_id =session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)
    #pl_id = session.query(Playlists.Id).filter(Playlists.Name == playlist, Playlists.Id.in_(playlists_id))
    #songs = session.query(Songs).filter(Songs.Id.in_(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==pl_id)))
    
    songs = session.query(PlaylistsSongs).filter(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==playlist.Id))
    
    playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))          
    
    return render_template("show_playlist.html", songs = songs, user=current_user, playlist=playlist, playlists=playlists)


@playlist_bp.route('/add_songs/<song_id>/<playlist>', methods=['GET', 'POST'])
@login_required
def add_songs(playlist, song_id):
    song_to_add = session.query(Songs).filter(Songs.Id == song_id).first()
    
    playlist_to_add = session.query(Playlists).filter(and_(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)), Playlists.Name == playlist)).first()
    
    playlist_to_add.songs.append(song_to_add)
    
    playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))
    
    session.commit()
   
    return redirect(url_for("playlist_bp.show_songs", playlist=playlist, playlists=playlists, user=current_user))

