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


#Route per visualizzare le playlist nella libreria

#A questa pagina ha accesso chiunque
#Semplicemente vengono collezionate le playlist dell'utente, utili anche a layout.html
#Oltre all'icona e al nome verranno visualizzati un bottone per eliminare e uno per modificare la playlist
#In cima alla pagina dei bottoni permettono di scorrere la libreria e passare ad altri contenuti
#Cliccando sull'icona o sul nome della playlist si viene indirizzati alla pagina della medesima
#dove se ne possono vedere il nome, la durata, quanti e quali brani vi sono, ed eventualmente toglierne/aggiungerne

@library_bp.route('/library')
@login_required
def library():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    return render_template("library.html", playlists=playlists, user=current_user)

 
#Route per visualizzare gli album a cui l'utente ha messo 'Mi piace' nella libreria

#A questa pagina ha accesso chiunque
#Semplicemente vengono collezionati gli album a cui l'utente ha messo 'Mi piace' e in una lista
#vengono inserite n-uple contenenti le informazioni da visualizzare come il nome, la durata, la casa discografica, ecc..
#Cliccando sull'icona o sul nome si viene reindirizzati alla pagina dell'album
#Cliccando sul nome dell'artista si viene reindirizzati alla pagina dell'artista
#In cima alla pagina dei bottoni permettono di scorrere la libreria e passare ad altri contenuti
   
@library_bp.route('/albums')
@login_required
def albums():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    albums = session.query(Albums).filter(Albums.Id.in_(session.query(Users_liked_Albums.album_id).filter(Users_liked_Albums.user_email==current_user.Email))) 
    
    lst_a=[]
    for a in albums:
        artist = session.query(Users).filter(Users.Email == a.Artist).first()
        lst_a.append([a.Name, artist.Name, a.Record_House, a.ReleaseDate, a.Duration, a.Id, artist.Email])
    return render_template("albums.html", playlists=playlists, user=current_user, albums=lst_a)


#Route per visualizzare le canzoni a cui l'utente ha messo 'Mi piace' nella libreria

#A questa pagina ha accesso chiunque
#Semplicemente vengono collezionate le canzoni a cui l'utente ha messo 'Mi piace' e in una lista
#vengono inserite n-uple contenenti le informazioni da visualizzare come il nome, la durata, gli album che la contengono, ecc..
#Cliccando sull'icona o sul nome si viene reindirizzati alla pagina della canzone
#Cliccando sul nome dell'artista si viene reindirizzati alla pagina dell'artista
#In cima alla pagina dei bottoni permettono di scorrere la libreria e passare ad altri contenuti
 
@library_bp.route('/songs')
@login_required
def songs():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])
        
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    songs = session.query(Songs).filter(Songs.Id.in_(session.query(Users_liked_Songs.song_id).filter(Users_liked_Songs.user_email==current_user.Email)))
    songs_id = session.query(Songs.Id).filter(Songs.Id.in_(session.query(Users_liked_Songs.song_id).filter(Users_liked_Songs.user_email==current_user.Email)))
    albums = session.query(Albums).filter(Albums.Id.in_(session.query(AlbumsSongs.album_id).filter(AlbumsSongs.song_id.in_(session.query(Songs.Id).filter(Songs.Id.in_(songs_id)))))).all()
    
    lst_s=[]
    for s in songs:
        artist = session.query(Users).filter(Users.Email == s.Artist).first()
        lst_s.append([s.Name, artist.Name, s.Genre, s.Duration, s.Id, artist.Email])
    
    return render_template("songs.html", playlists=playlists, user=current_user, songs=lst_s, albums=albums)