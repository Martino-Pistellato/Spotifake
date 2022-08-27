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
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
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
    pl_id = session.query(Playlists.Id).filter(Playlists.User==current_user.Email, Playlists.Name == playlist_name)
    songs = session.query(Songs).filter(Songs.Id.not_in(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==pl_id)))
    if(current_user.Profile == 'Free'):
        songs = session.query(Songs).filter(Songs.Id.not_in(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==pl_id)), Songs.Is_Restricted==False)
   
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)     
    
    return render_template("add_songs.html", songs = songs, user = current_user, playlist = playlist_name, playlists = playlists)

@playlist_bp.route('/show_playlist_content/<playlist_name>', methods=['GET', 'POST'])
@login_required
def show_playlist_content(playlist_name):
    pl = session.query(Playlists).filter(Playlists.User==current_user.Email, Playlists.Name == playlist_name).first()
    songs = session.query(Songs).filter(Songs.Id.in_(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==pl.Id)))
    
    #songs = session.query(PlaylistsSongs).filter(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==playlist.Id))
    
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    
    return render_template("show_playlist_content.html", songs = songs, user = current_user, playlist = pl, playlists = playlists)


@playlist_bp.route('/add_songs/<song_id>/<playlist>', methods=['GET', 'POST'])
@login_required
def add_songs(playlist, song_id):
    song = session.query(Songs).filter(Songs.Id == song_id).first()
    playlist = session.query(Playlists).filter(Playlists.User==current_user.Email, Playlists.Name == playlist).first()
    Playlists.add_song_to_playlist(playlist, song)
   
    return redirect(url_for("playlist_bp.show_songs_addable", playlist_name=playlist.Name))

@playlist_bp.route('/delete_playlist/<pl_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def delete_playlist(pl_id):
    Playlists.delete_playlist(pl_id)

    return redirect(url_for("library_bp.library"))

@playlist_bp.route('/edit_playlist/<pl_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def edit_playlist(pl_id):
    pl = session.query(Playlists).filter(Playlists.Id == pl_id).first()
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        
    return render_template("edit_playlist.html", user=current_user, playlists=playlists, name=pl.Name, id=pl_id)

@playlist_bp.route('/update_playlist/<pl_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def update_playlists(pl_id):
    if request.method == 'POST':
        name = request.form["name"]
        Playlists.update_playlist(pl_id, name)
                    
        return redirect(url_for("library_bp.library"))

@playlist_bp.route('/remove_song/<song_id>/<pl_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def remove_song(song_id, pl_id):
    playlist = session.query(Playlists).filter(Playlists.Id == pl_id).first()
    Playlists.remove_song(playlist, song_id)

    return redirect(url_for("playlist_bp.show_playlist_content", playlist_name = playlist.Name))