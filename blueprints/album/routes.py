from flask import Blueprint, render_template, request
from flask import current_app as app
from blueprints.models import *


# Blueprint Configuration
album_bp = Blueprint(
    'album_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@album_bp.route('/album')
def album(album):
    conn = engine.connect()
    songs = conn.execute(select([Songs]).where(Songs.albums == album.Id)).fetchall()
    albums = conn.execute(select([Albums]).where(Albums.artist == album.artist))
    conn.close()
    n_songs = songs.__sizeof__
    render_template("album.html",
                    user = current_user, 
                    album = album,
                    songs = songs,
                    albums = albums,
                    n_songs = n_songs
    )