from flask import Blueprint, render_template, request
from flask import current_app as app
from blueprints.models import *


# Blueprint Configuration
album_bp = Blueprint(
    'album_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@album_bp.route('/album/<album>')
def album(album):
    conn = engine.connect()
    songs = conn.execute(select([Songs]).where(Songs.albums == album.Id)).fetchall()
    albums = conn.execute(select([Albums]).where(Albums.artist == album.artist))
    playlists = conn.execute(select([Playlists]).where(Playlists.Id.in_(select([PlaylistsUsers.playlist_id]).where(PlaylistsUsers.user_email==current_user.Email))))
    
    #playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))
    conn.close()
    n_songs = songs.__sizeof__
    
    return render_template("album.html",
                    user = current_user, 
                    album = album,
                    songs = songs,
                    albums = albums,
                    n_songs = n_songs,
                    playlists = playlists
    )