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

#Route per raccogliere e mostrare informazioni sull'artista, quali il nome, l'età, il paese, 
#il numero di brani e album pubblicati (questi numeri dipendono dal tipo di utente che accede alla pagina: per un
#utente Free verranno conteggiati solo i contenuti pubblici)

#A questa pagina ha accesso chiunque

@artist_bp.route('/show_artist/<artist_email>')
@login_required
def show_artist(artist_email):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
        songs = session.query(Songs).filter(Songs.Artist == artist_email).all()
        albums = session.query(Albums).filter(Albums.Artist == artist_email).all()

    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
        songs = session.query(Songs).filter(Songs.Artist == artist_email).all()
        albums = session.query(Albums).filter(Albums.Artist == artist_email).all()

    else:
        session = Session(bind=engine["free"])
        songs = session.query(Songs).filter(Songs.Artist == artist_email, Songs.Is_Restricted == False).all()
        albums = session.query(Albums).filter(Albums.Artist == artist_email, Albums.Is_Restricted == False).all()
    
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    artist = session.query(Artists).filter(Artists.Email == artist_email).first()

    n_songs=len(songs)
    n_albums=len(albums)
    age = date.today() - relativedelta(years=artist.BirthDate.year, months=artist.BirthDate.month, days=artist.BirthDate.day)

    return render_template("show_artist.html", playlists=playlists, user=current_user, artist=artist, songs=songs, albums=albums, age=age.year, n_songs=n_songs, n_albums=n_albums)