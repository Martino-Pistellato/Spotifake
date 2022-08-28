from flask import Blueprint, render_template, redirect, url_for, request
from flask import current_app as app
from flask_login import *
from blueprints.models import *

# Blueprint Configuration
library_bp = Blueprint(
    'library_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@library_bp.route('/library')
@login_required
def library():
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    return render_template("library.html", playlists=playlists, user=current_user)
    
@library_bp.route('/albums')
@login_required
def albums():
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    albums = session.query(Albums).filter(Albums.Id.in_(session.query(Users_liked_Albums.album_id).filter(Users_liked_Albums.user_email==current_user.Email))) 
    return render_template("albums.html", playlists=playlists, user=current_user, albums=albums)

@library_bp.route('/artists')
@login_required
def artists():
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    #artists = session.query(Users).filter(Users.Email.in_()) -- è possibile avere degli artisti salvati?
    return render_template("artists.html", playlists=playlists, user=current_user)
    
@library_bp.route('/songs')
@login_required
def songs():
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    songs = session.query(Songs).filter(Songs.Id.in_(session.query(Users_liked_Songs.song_id).filter(Users_liked_Songs.user_email==current_user.Email)))
    songs_id = session.query(Songs.Id).filter(Songs.Id.in_(session.query(Users_liked_Songs.song_id).filter(Users_liked_Songs.user_email==current_user.Email)))
    albums = session.query(Albums).filter(Albums.Id.in_(session.query(AlbumsSongs.album_id).filter(AlbumsSongs.song_id.in_(session.query(Songs.Id).filter(Songs.Id.in_(songs_id)))))).all()
    return render_template("songs.html", playlists=playlists, user=current_user, songs=songs, albums=albums)