from flask import Blueprint, render_template, redirect, url_for, flash
from flask import current_app as app
from flask_login import *
from blueprints.models import *
from datetime import timedelta
import datetime
from ..forms import upload_PlaylistForm
from sqlescapy import sqlescape
from sqlalchemy import exc

# Blueprint Configuration
playlist_bp = Blueprint(
    'playlist_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

#Route per caricare una playlist sull'applicazione

#A questa pagina ha accesso chiunque
#Nel blocco try..except.., nel blocco try, vengono caricate le informazioni necessarie al caricamento della playlist,
#prese dall'apposito form
#Se tutte le informazioni sono ammesse, viene creata la playlist,che viene poi associata all'utente che l'ha creata e 
#si può passare all'inserimento delle canzoni
#Se le informazioni non sono ammesse, e questo avviene quando 1)il nome della playlist eccede i 10 ch (gestito dal form)
#                                                             2)il nome della playlist è uguale a quello di una playlist 
#                                                               già esistente e caricata dal medesimo utente (gestito dal blocco except)
#si resterà sulla pagina dedicata al form, che mostrerà specifici messaggi d'errore


@playlist_bp.route('/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])
    
    try:

        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        form = upload_PlaylistForm()
        
        if form.validate_on_submit():
            user = session.query(Users).filter(Users.Email == current_user.Email).first()
            playlist = Playlists(sqlescape(form.name.data))
            Playlists.create_playlist(playlist, session)# crea playlist nel DB
            Users.add_playlist(user, playlist, session)#associa playlist e utente
            
            return redirect(url_for("playlist_bp.show_songs_addable", playlist_id=playlist.Id))
        return render_template('playlist.html', form=form, user=current_user, playlists=playlists)
    
    except exc.SQLAlchemyError as err:
        session.rollback()
        flash(err.orig.diag.message_primary, 'error')
        return render_template('playlist.html', form=form, user=current_user, playlists=playlists)


#Route che raccoglie e mostra le canzoni che possono essere aggiunte alla playlist. 

#A questa pagina ha accesso chiunque, ma se si accede a questa funzionalità per una playlist non propria si viene
#rimandati alla home.
#Tramite una query si risale a tutte le canzoni presenti nell'applicazione (solo pubbliche se si è Free, non quelle dell'artista 
#se l'utente è Artist) e non inserite in questa specifica playlist (questa route viene usata per aggiungere brani 
#alla playlist in generale)
#Oltre alle informazioni generali sulla canzone, viene visualizzato un pulsante che ne permette l'aggiunta

@playlist_bp.route('/show_songs_addable/<playlist_id>', methods=['GET', 'POST'])
@login_required
def show_songs_addable(playlist_id):
    if(current_user.Profile == 'Artist'):#l'artista non aggiunge proprie canzoni alla playlist
        session = Session(bind=engine["artist"])
        songs = session.query(Songs).filter(Songs.Artist != current_user.Email, Songs.Id.not_in(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==playlist_id)))
    
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
        songs = session.query(Songs).filter(Songs.Id.not_in(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==playlist_id)))
    
    else:
        session = Session(bind=engine["free"])#l'utente Free non aggiunge canzoni Premium
        songs = session.query(Songs).filter(Songs.Id.not_in(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==playlist_id)), Songs.Is_Restricted==False)
    
    pl = session.query(Playlists).filter(Playlists.Id == playlist_id).first()

    if(pl.User != current_user.Email):#se la playlist non è dell'utente, torna alla home
        return redirect(url_for("home_bp.home"))

    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)     
    
    return render_template("add_songs.html", songs = songs, user = current_user, playlist = pl, playlists = playlists)

#Route per collezionare e vedere le canzoni presenti nella playlist

#A questa pagina ha accesso chiunque, ma se si accede ad una playlist non propria si viene rimandati alla home
#Una volta collezionate infromazioni riguardanti la playlist e le canzoni in essa contenute
#si viene reindirizzati alla pagina della playlist, di cui vengono mostrati titolo, durata, quanti e quali brani
#vi sono inseriti.
#Viene data la possibilità di toglierne/aggiungerne

@playlist_bp.route('/show_playlist_content/<playlist_id>', methods=['GET', 'POST'])
@login_required
def show_playlist_content(playlist_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    pl = session.query(Playlists).filter(Playlists.Id==playlist_id).first()

    if(pl.User != current_user.Email):#se la playlist non è dell'utente, torna alla home
        return redirect(url_for("home_bp.home"))

    #trova canzoni inserite nella playlist
    songs = session.query(Songs).filter(Songs.Id.in_(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==pl.Id))).all()
  
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    n_songs = len(songs)
    return render_template("show_playlist_content.html", songs = songs, user = current_user, playlist = pl, playlists = playlists, n_songs = n_songs)

#Route per aggiungere una canzone alla playlist

#A questa funzionalità ha accesso chiunque, ma se si accede ad una playlist non propria si viene rimandati alla home
#Una volta individuate la canzone e la playlist specifiche, la durata della playlist viene aggiornata aggiungendo 
#la durata della canzone, che viene poi inserita nella playlist

@playlist_bp.route('/add_songs/<song_id>/<playlist_id>', methods=['GET', 'POST'])
@login_required
def add_songs(song_id, playlist_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])
    
    song = session.query(Songs).filter(Songs.Id == song_id).first()
    playlist = session.query(Playlists).filter(Playlists.Id==playlist_id).first()

    if(playlist.User != current_user.Email):#se la playlist non è dell'utente, torna alla home
        return redirect(url_for("home_bp.home"))

    st = song.Duration
    pt = playlist.Duration

    start = datetime.datetime(10, 10, 10, hour=pt.hour, minute=pt.minute, second=pt.second)#tempo iniziale
    add = datetime.timedelta(seconds=st.second, minutes=st.minute, hours=st.hour)#tempo da aggiungere
    end = start + add #tempo finale

    #aggiorna ed inserisce
    Playlists.update_playlist(playlist_id, playlist.Name, end.time(), session)
    Playlists.add_song_to_playlist(playlist, song, session)
   
    return redirect(url_for("playlist_bp.show_songs_addable", playlist_id=playlist.Id))

#Route per cancellare una playlist

#A questa funzionalità ha accesso chiunque, ma se si accede ad una playlist non propria si viene rimandati alla home
#Dopo gli opportuni controlli, viene richiamata la funzione apposita in Playlists

@playlist_bp.route('/delete_playlist/<pl_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def delete_playlist(pl_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])
    
    playlist = session.query(Playlists).filter(Playlists.Id==pl_id).first()

    if(playlist.User != current_user.Email):#se la playlist non è dell'utente, torna alla home
        return redirect(url_for("home_bp.home"))
    
    Playlists.delete_playlist(pl_id, session)

    return redirect(url_for("library_bp.library"))

#Route per modificare una playlist

#A questa funzionalità ha accesso chiunque, ma se si accede ad una playlist non propria si viene rimandati alla home
#Nel blocco try..except.., nel blocco try, vengono caricate le informazioni necessarie ala modifica della playlist,
#prese dall'apposito form
#Se tutte le informazioni sono ammesse, viene modificata la playlist
#Se le informazioni non sono ammesse, e questo avviene quando 1)il nome della playlist eccede i 10 ch (gestito dal form)
#                                                             2)il nome della playlist è uguale a quello di una playlist 
#                                                               già esistente e caricata dal medesimo utente (gestito dal blocco except)
#si resterà sulla pagina dedicata al form, che mostrerà specifici messaggi d'errore


@playlist_bp.route('/edit_playlist/<pl_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def edit_playlist(pl_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    try:
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        pl = session.query(Playlists).filter(Playlists.Id == pl_id).first()

        if(pl.User != current_user.Email): #se la playlist non è dell'utente, torna alla home
            return redirect(url_for("home_bp.home"))
        
        form = upload_PlaylistForm(name=pl.Name)
        
        if form.validate_on_submit():
            Playlists.update_playlist(pl_id, sqlescape(form.name.data), pl.Duration, session)
                        
            return redirect(url_for("library_bp.library"))
            
        return render_template("edit_playlist.html", user=current_user, playlists=playlists, name=pl.Name, id=pl_id, form=form)

    except exc.SQLAlchemyError as err:
        session.rollback()
        flash(err.orig.diag.message_primary, 'error')
        return render_template("edit_playlist.html", user=current_user, playlists=playlists, name=pl.Name, id=pl_id, form=form)



#Route per rimuovere una canzone dalla playlist

#A questa funzionalità ha accesso chiunque, ma se si accede ad una playlist non propria si viene rimandati alla home
#Una volta individuate la canzone e la playlist specifiche, la durata della playlist viene aggiornata sottraendo 
#la durata della canzone, che viene poi rimossa dalla playlist

@playlist_bp.route('/remove_song/<song_id>/<pl_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def remove_song(song_id, pl_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    playlist = session.query(Playlists).filter(Playlists.Id == pl_id).first()

    if(playlist.User != current_user.Email):#se la playlist non è dell'utente, torna alla home
        return redirect(url_for("home_bp.home"))
    
    
    song=session.query(Songs).filter(Songs.Id == song_id).first()

    st = song.Duration
    pt = playlist.Duration

    start = datetime.datetime(10, 10, 10, hour=pt.hour, minute=pt.minute, second=pt.second)#tempo iniziale
    minus = datetime.timedelta(seconds=st.second, minutes=st.minute, hours=st.hour)#tempo da sottrarre
    end = start - minus #tempo finale

    #aggiorna e rimuove
    Playlists.update_playlist(pl_id, playlist.Name, end.time(), session)
    Playlists.remove_song(playlist, song_id, session)

    return redirect(url_for("playlist_bp.show_playlist_content", playlist_id = playlist.Id))