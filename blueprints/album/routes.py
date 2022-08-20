from flask import Blueprint, render_template
from flask import current_app as app
from sqlalchemy import *
from blueprints.models import *

# Blueprint Configuration
album_bp = Blueprint(
    'album_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

album_bp.route('/album')
def album_home(album_title):
    conn = engine.connect()
    res = conn.execute(select([Songs.Name, Songs.Duration]).where(Songs.albums == album_title))
    songs = res.fetchall()
    render_template("album.html", songs = songs, album_title = album_title)