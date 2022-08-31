from datetime import date
import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template, redirect, url_for, request
from flask import current_app as app
from flask_login import *
from blueprints.models import *

# Blueprint Configuration
artist_bp = Blueprint(
    'artist_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@artist_bp.route('/show_artist/<artist_email>')
@login_required
def show_artist(artist_email):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])
    
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    artist = session.query(Artists).filter(Artists.Email == artist_email).first()

    if(current_user.Profile == "Free"):
        songs = session.query(Songs).filter(Songs.Artist == artist_email, Songs.Is_Restricted == False).all()
        albums = session.query(Albums).filter(Albums.Artist == artist_email, Albums.Is_Restricted == False).all()
    else:
        songs = session.query(Songs).filter(Songs.Artist == artist_email).all()
        albums = session.query(Albums).filter(Albums.Artist == artist_email).all()


    n_songs=len(songs)
    n_albums=len(albums)
    age = date.today() - relativedelta(years=artist.BirthDate.year, months=artist.BirthDate.month, days=artist.BirthDate.day)

    return render_template("show_artist.html", playlists=playlists, user=current_user, artist=artist, songs=songs, albums=albums, age=age.year, n_songs=n_songs, n_albums=n_albums)