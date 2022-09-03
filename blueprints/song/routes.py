from re import template
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import *
from blueprints.models import *
import datetime
from ..forms import upload_SongForm
from sqlescapy import sqlescape
from sqlalchemy import exc

# Blueprint Configuration
song_bp = Blueprint(
    'song_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


#Route per caricare una canzone sull'applicazione

#Solo gli artisti possono creare contenuti. Se un utente Free o Premium dovesse in qualche modo accedere a questa 
#funzionalità, verrebbe rimandato alla home. 
#Nel blocco try..except.., nel blocco try, vengono caricate le informazioni necessarie al caricamento della canzone,
#prese dall'apposito form
#Se tutte le informazioni sono ammesse, viene creata la canzone, caricata sul DB, associato all'artista che l'ha creata e 
#l'utente viene reindirizzato alla pagina contente le sue canzoni
#Se le informazioni non sono ammesse, e questo avviene quando 1)il nome della canzone eccede i 10 ch (gestito dal form)
#                                                             2)il nome della canzone è uguale a quello di una canzone 
#                                                               già esistente e caricata dal medesimo artista (gestito dal blocco except)
#si resterà sulla pagina dedicata al form, che mostrerà specifici messaggi d'errore


@song_bp.route('/upload_song', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def upload_song():
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"])

    try:
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        form = upload_SongForm()
        
        if form.validate_on_submit():
            name = sqlescape(form.name.data)
            time = form.time.data
            genre = form.genre.data
            if form.type.data == 'Premium':
                restriction = True
            else:
                restriction = False  
            song = Songs(name, time, genre, restriction, current_user.Email)
            artist = session.query(Artists).filter(Artists.Email == current_user.Email).first()
            Songs.create_song(song, session)
            Artists.add_song_if_artist(artist, song, session)
                
            return redirect(url_for("song_bp.show_my_songs", user=current_user, playlists=playlists))    
        return render_template('upload_song.html',form=form, user=current_user, playlists=playlists)

    except exc.SQLAlchemyError as err:
        session.rollback()
        flash(err.orig.diag.message_primary, 'error') 
        return render_template('upload_song.html',form=form, user=current_user, playlists=playlists)
    

#Route per modificare una canzone

#Se un utente Free o Premium dovesse in qualche modo accedere a questa funzionalità, verrebbe rimandato alla home.
#Lo stesso avviene se un artista dovesse accedere a questa funzionalità per una canzone non sua.
#Nel blocco try..except.., nel blocco try, vengono caricate le informazioni necessarie alla modifica della canzone,
#prese dall'apposito form
#Se tutte le informazioni sono ammesse, viene modificata la canzone.
#Da notare che, nel caso in cui la canzone fosse originariamente un contenuto Free che tramite modifica viene
#alzato a contenuto Premium, da eventuali album Free che la contengono la canzone viene rimossa, e le durate di
#ciascuno si aggiornano di conseguenza
#Se le informazioni non sono ammesse, e questo avviene quando 1)il nome della canzone eccede i 10 ch (gestito dal form)
#                                                             2)il nome della canzone è uguale a quello di una canzone 
#                                                               già esistente e caricata dal medesimo artista (gestito dal blocco except)
#si resterà sulla pagina dedicata al form, che mostrerà specifici messaggi d'errore


@song_bp.route('/edit_song/<song_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def edit_song(song_id):
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"]) 
        
    try:
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        song = session.query(Songs).filter(Songs.Id == song_id).first()
        if(song.Artist != current_user.Email):
            return redirect(url_for("home_bp.home"))
           
        if song.Is_Restricted == True:
            restriction = 'Premium'
        else:
            restriction = 'Free'
        
        form = upload_SongForm(name=song.Name, time=song.Duration, genre=song.Genre, type = restriction)
        
        if form.validate_on_submit():
            name = sqlescape(form.name.data)
            time = form.time.data
            genre = form.genre.data
            if form.type.data == 'Premium':
                restriction = True
            else:
                restriction = False  
            
            if(song.Is_Restricted == False and restriction):
                albums = session.query(Albums).filter(Albums.Id.in_(session.query(AlbumsSongs.album_id).filter(AlbumsSongs.song_id==song_id)), Albums.Is_Restricted==False)
                st = song.Duration
                date = datetime.date(10, 10, 10)
                for a in albums:
                    at = a.Duration
                    start = datetime.datetime.combine(date, at)
                    minus = datetime.timedelta(seconds=st.second, minutes=st.minute, hours=st.hour)
                    end = start - minus

                    Albums.remove_song(a, song_id, session)

                    Albums.update_album(a.Id, a.Name, a.ReleaseDate, a.Record_House, end.time(), a.Is_Restricted, session)

            Songs.update_song(song_id, name, time, genre, restriction, session)
                
            return redirect(url_for("song_bp.show_my_songs", user=current_user, playlists=playlists)) 
            
        return render_template("edit_song.html", user=current_user, playlists=playlists, id=song_id, form=form)

    except exc.SQLAlchemyError as err:
        session.rollback()
        flash(err.orig.diag.message_primary, 'error') 
        return render_template("edit_song.html", user=current_user, playlists=playlists, id=song_id, form=form)
            


#Route per eliminare una canzone

#Se un utente Free o Premium dovesse in qualche modo accedere a questa funzionalità, verrebbe rimandato alla home.
#Lo stesso avviene se un artista dovesse accedere a questa funzionalità per una canzone non sua.
#Innanzitutto, se una canzone viene eliminata, le playlist e gli album che la contengono vanno aggiornati di conseguenza.
#Le loro durate vengono quindi aggiornate sottraendo il tempo della canzone
#Viene poi chiamata l'opportuna funzione in Songs

@song_bp.route('/delete_song/<song_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def delete_song(song_id):
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"]) 

    albums = session.query(Albums).filter(Albums.Id.in_(session.query(AlbumsSongs.album_id).filter(AlbumsSongs.song_id==song_id)))
    playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsSongs.playlist_id).filter(PlaylistsSongs.song_id==song_id)))
    song=session.query(Songs).filter(Songs.Id == song_id).first()

    if(song.Artist != current_user.Email):
        return redirect(url_for("home_bp.home"))
            
    st = song.Duration
    minus = datetime.timedelta(seconds=st.second, minutes=st.minute, hours=st.hour)
    date = datetime.date(10, 10, 10)
        
    for a in albums:
        start=datetime.datetime.combine(date, a.Duration)
        end = start - minus
        Albums.update_album(a.Id, a.Name, a.ReleaseDate, a.Record_House, end.time(), a.Is_Restricted, session)

    for p in playlists:
        start=datetime.datetime.combine(date, p.Duration)
        end = start - minus
        Playlists.update_playlist(p.Id, p.Name, end.time(), session)

    Songs.delete_song(song_id, session)
    return redirect(url_for("song_bp.show_my_songs"))

#Route per raccogliere e mostrare tutti le canzoni di un artista

#Se un utente Free o Premium dovesse in qualche modo accedere a questa funzionalità, verrebbe rimandato alla home.
#Tramite due query vengono collezionate le canzoni pubbliche e le canzoni premium dell'artista che accede alla pagina
#Nella pagina verrano visualizzate adeguatamente separate nelle due categorie
#Oltre all'icona e al nome della canzone, vengono visualizzati anche un bottone per eliminare e uno per modificare la canzone
#In cima alla pagina un bottone da la possibilità di creare nuovi album

@song_bp.route('/show_my_songs')
@login_required # richiede autenticazione
def show_my_songs():
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"]) 

    songs_free = session.query(Songs).filter(Songs.Artist == current_user.Email, Songs.Is_Restricted == False)
    songs_premium = session.query(Songs).filter(Songs.Artist == current_user.Email, Songs.Is_Restricted == True)
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    
    return render_template("show_my_songs.html", songs_free = songs_free, songs_premium = songs_premium, user = current_user, playlists = playlists)



#Route per mettere 'Mi piace' ad una canzone

#A questa funzionalità ha accesso chiunque
#Prima di effettuare l'azione e modificare il numero di 'Mi piace' della canzone, è opportuno controllare che
#l'utente in questione non abbia già messo 'Mi piace' alla canzone, in modo che utenti malintenzionati
#non accedano a questa funzionalià in maniera diretta andando a pompare o sgonfiare i 'Mi piace' a loro piacimento

@song_bp.route('/add_to_liked_songs/<song_id>/<int:page>')
@login_required # richiede autenticazione
def add_to_liked_songs(song_id, page):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    song = session.query(Songs).filter(Songs.Id == song_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()

    if(session.query(Users_liked_Songs).filter(Users_liked_Songs.song_id == song_id, Users_liked_Songs.user_email==user.Email).first() is None):
        Users.add_song_to_liked(user, song, session)
        Songs.update_likes(song.N_Likes + 1, song_id, session)

    if(page == 1):
        return redirect(url_for("find_bp.find"))
    else:
        return redirect(url_for("song_bp.show_song", song_id=song_id))

#Route per togliere 'Mi piace' ad una canzone

#A questa funzionalità ha accesso chiunque
#Prima di effettuare l'azione e modificare il numero di 'Mi piace' della canzone, è opportuno controllare che
#l'utente in questione abbia già messo 'Mi piace' alla canzone, in modo che utenti malintenzionati
#non accedano a questa funzionalià in maniera diretta andando a pompare o sgonfiare i 'Mi piace' a loro piacimento

@song_bp.route('/remove_from_liked_songs/<song_id>/<int:page>')
@login_required # richiede autenticazione
def remove_from_liked_songs(song_id, page):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])
        
    song = session.query(Songs).filter(Songs.Id == song_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()

    if(session.query(Users_liked_Songs).filter(Users_liked_Songs.song_id == song_id, Users_liked_Songs.user_email==user.Email).first() is not None):
        Users.remove_song_from_liked(user, song_id, session)
        Songs.update_likes(song.N_Likes - 1, song_id, session)

    if(page == 1):
        return redirect(url_for("find_bp.find"))
    else:
        return redirect(url_for("song_bp.show_song", song_id=song_id))


#Route per visualizzare la pagina contenente alcune informazioni di una canzone, come il titolo, l'artista, la durata, 
#il genere ed il numero di 'Mi piace'

#A questa pagina ha accesso chiunque
#Se l'utente visualizza la pagina inerente ad una canzone non sua, ha la possibilità di mettere 'Mi piace'

@song_bp.route('/show_song/<song_id>')
@login_required # richiede autenticazione
def show_song(song_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    song = session.query(Songs).filter(Songs.Id==song_id).first()
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)

    if session.query(Users_liked_Songs).filter(Users_liked_Songs.song_id==song.Id, Users_liked_Songs.user_email==current_user.Email).first() is None:
        like = False
    else:
        like = True
    artist = session.query(Users).filter(Users.Email==song.Artist).first()
    
    return render_template('show_song.html', user=current_user, playlists=playlists, song=song, artist_name=artist.Name, like=like)