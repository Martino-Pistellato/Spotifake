from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app as app
from blueprints.models import *
from flask_login import *


# Blueprint Configuration
album_bp = Blueprint(
    'album_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@album_bp.route('/album')
@login_required
def album():
    if(current_user.Profile == 'Artist'):
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)        
        return render_template("album.html", user=current_user, playlists=playlists)


@album_bp.route('/create_album', methods=['GET', 'POST'])
@login_required
def create_album():
    if(current_user.Profile == 'Artist'):
        if request.method == 'POST':
            name = request.form["name"]
            record_house = request.form["record_h"]
            date = request.form["date"]
            if (name is not None and date is not None and record_house is not None):
                album = Albums(name, date, '00:00:00', record_house, current_user.Email)
                Albums.create_album(album)
                user = session.query(Users).filter(Users.Email == current_user.Email).first()
                Users.add_album_if_artist(user, album)
                return redirect(url_for("album_bp.show_songs_addable_album", album_name=name))

@album_bp.route('/show_songs_addable_album/<album_name>', methods=['GET', 'POST'])
@login_required
def show_songs_addable_album(album_name):
    if(current_user.Profile == 'Artist'):
        album = session.query(Albums).filter(and_(Albums.Name == album_name, Albums.Artist == current_user.Email)).first()
        all_my_songs = session.query(Songs.Id).filter(Songs.Artist == current_user.Email)
        my_songs_in_album = session.query(Songs.Id).filter(Songs.Id.in_(session.query(AlbumsSongs.song_id).filter(AlbumsSongs.album_id == album.Id)))
        my_songs = session.query(Songs).filter(Songs.Id.not_in(my_songs_in_album), Songs.Id.in_(all_my_songs))
        playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))
        
        return render_template("show_songs_album.html", album=album_name, user=current_user, playlists=playlists, songs=my_songs)


@album_bp.route('/add_songs_to_album/<song_id>/<album_name>', methods=['GET', 'POST'])
@login_required
def add_songs_to_album(song_id, album_name):
    if(current_user.Profile == 'Artist'):
        song = session.query(Songs).filter(Songs.Id == song_id).first()
        album = session.query(Albums).filter(Albums.Name == album_name).first()
        Albums.add_song_to_album(album, song)

        #SISTEMARE DURATA DELL'ALBUM!!!
        
        Albums.update_album(album.Id, album.Name, album.ReleaseDate, album.Duration, album.Record_House, album.Artist)

        return redirect(url_for("album_bp.show_songs_addable_album", album_name=album_name))

@album_bp.route('/show_my_albums')
@login_required
def show_my_albums():
    if(current_user.Profile == 'Artist'):
       albums = session.query(Albums).filter(Albums.Artist == current_user.Email)
       playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))
       
       return render_template("show_my_albums.html", user=current_user, playlists=playlists, albums=albums)


@album_bp.route('/show_album/<album_name>/<artist>')
@login_required
def show_album(album_name, artist):
    album = session.query(Albums).filter(Albums.Name == album_name, Albums.Artist == artist).first()
    artist_name = session.query(Users.Name).filter(Users.Email == artist).first()
    songs = session.query(Songs).filter(Songs.Id.in_(session.query(AlbumsSongs.song_id).filter(AlbumsSongs.album_id == album.Id)))
    albums = session.query(Albums).filter(Albums.Artist == artist, Albums.Id != album.Id)
    playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))
    n_songs = songs.__sizeof__
    
    return render_template("show_album.html",
                    user = current_user, 
                    album = album,
                    songs = songs,
                    albums = albums,
                    n_songs = n_songs,
                    playlists = playlists,
                    artist_name = artist_name
    )