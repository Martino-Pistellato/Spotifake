from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import current_app as app
from blueprints.models import *
from flask_login import *
from ..forms import upload_AlbumForm
import datetime
from sqlescapy import sqlescape

# Blueprint Configuration
album_bp = Blueprint(
    'album_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


#Route per caricare un album sull'applicazione

#Solo gli artisti possono creare contenuti. Se un utente Free o Premium dovesse in qualche modo accedere a questa 
#funzionalità, verrebbe rimandato alla home. 
#Nel blocco try..except.., nel blocco try, vengono caricate le informazioni necessarie al caricamento dell'album,
#prese dall'apposito form
#Se tutte le informazioni sono ammesse, viene creato l'album, caricato sul DB, associato all'artista che l'ha creato e 
#si può passare all'inserimento delle canzoni
#Se le informazioni non sono ammesse, e questo avviene quando 1)il nome dell'album eccede i 10 ch (gestito dal form)
#                                                             2)il nome dell'album è uguale a quello di un album 
#                                                               già esistente e caricato dal medesimo artista (gestito dal blocco except)
#si resterà sulla pagina dedicata al form, che mostrerà specifici messaggi d'errore

@album_bp.route('/create_album', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def create_album():
    if(current_user.Profile != 'Artist'):           
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"]) #apre una sessione con il DB con ruolo Artist

    try:
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email) #informazione necessaria per layout.html
        
        form = upload_AlbumForm() 
            
        if form.validate_on_submit(): 
            name = sqlescape(form.name.data) #unico input al 100% dell'utente, viene usato l'escaping per sanificare
            rec_h = form.recordHouse.data
            if form.type.data == 'Premium':
                restriction = True
            else:
                restriction = False
                    
            album = Albums(name, rec_h, current_user.Email, restriction) 
            artist = session.query(Artists).filter(Artists.Email == current_user.Email).first() 
            Albums.create_album(album, session) 
            Artists.add_album_if_artist(artist, album, session) 
                
            return redirect(url_for("album_bp.show_songs_addable_album", album_id = album.Id)) 
        return render_template('create_album.html',form=form, user=current_user, playlists=playlists) 

    except exc.SQLAlchemyError as err:
        session.rollback()
        flash(err.orig.diag.message_primary, 'error')
        return render_template('create_album.html',form=form, user=current_user, playlists=playlists)
    

#Route che raccoglie e mostra le canzoni che possono essere aggiunte all'album. 

#Se un utente Free o Premium dovesse in qualche modo accedere a questa funzionalità, verrebbe rimandato alla home.
#Lo stesso avviene se un artista dovesse accedere a questa funzionalità per un album non suo.
#Tramite due query si risale a tutte le canzoni dell'artista e a quelle che sono già contenute nell'album (questa route viene usata per
#aggiungere brani all'album in generale), e tramite una terza query vengono trovate quelle che l'artista può inserire, guardando anche 
#se il contenuto è Premium o meno)
#N.B. un artista può creare un album solo con proprie canzoni

@album_bp.route('/show_songs_addable_album/<album_id>', methods=['GET', 'POST'])
@login_required
def show_songs_addable_album(album_id):
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"])
    
    album = session.query(Albums).filter(and_(Albums.Id == album_id)).first()

    if(album.Artist != current_user.Email):
        return redirect(url_for("home_bp.home"))

    all_my_songs = session.query(Songs.Id).filter(Songs.Artist == current_user.Email)
    my_songs_in_album = session.query(Songs.Id).filter(Songs.Id.in_(session.query(AlbumsSongs.song_id).filter(AlbumsSongs.album_id == album.Id)))
    
    if(album.Is_Restricted == False):
        my_songs = session.query(Songs).filter(Songs.Id.not_in(my_songs_in_album), Songs.Id.in_(all_my_songs), Songs.Is_Restricted == False)
    else:
        my_songs = session.query(Songs).filter(Songs.Id.not_in(my_songs_in_album), Songs.Id.in_(all_my_songs))
       
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        
    return render_template("show_songs_album.html", album=album, user=current_user, playlists=playlists, songs=my_songs)


#Route per aggiungere canzoni all'album

#Se un utente Free o Premium dovesse in qualche modo accedere a questa funzionalità, verrebbe rimandato alla home.
#Lo stesso avviene se un artista dovesse accedere a questa funzionalità per un album o una canzone non suoi.
#Nel blocco try..catch.., nel blocco try, vengono trovate la canzone e l'album specifici, il tempo dell'album
#viene aggiornato aggiungendo il tempo della canzone e la canzone viene aggiunta all'album
#Nel blocco except viene gestito l'errore nel caso in cui aggiungendo un brano si sforasse il tempo limite di un album
#fissato a 1.30h
#In entrambi i casi si resta sulla pagina che mostra i brani che si possono aggiungere
#Se l'operazione è andata a buon fine la canzone sarà nell'album e non apparirà più fra le aggiungibili
#Altrimenti sarà ancora lì e un verrà mostrato un messaggio d'errore

@album_bp.route('/add_songs_to_album/<song_id>/<album_id>', methods=['GET', 'POST'])
@login_required
def add_songs_to_album(song_id, album_id):
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"])

    try:
        song = session.query(Songs).filter(Songs.Id == song_id).first()
        album = session.query(Albums).filter(Albums.Id == album_id).first()

        if(album.Artist != current_user.Email or song.Artist != current_user.Email):
            return redirect(url_for("home_bp.home"))

        
        st = song.Duration
        at = album.Duration
        
        start = datetime.datetime(10, 10, 10, hour=at.hour, minute=at.minute, second=at.second)
        add = datetime.timedelta(seconds=st.second, minutes=st.minute, hours=st.hour)
        end = start + add
        
        Albums.update_album(album.Id, album.Name, album.ReleaseDate,album.Record_House, end.time(), album.Is_Restricted, session)
        Albums.add_song_to_album(album, song, session)

    except exc.SQLAlchemyError as err:
        session.rollback()
        flash('Un album può avere una durata massima di 1:30:00', 'error')
        flash('Aggiungendo questo brano il tuo album avrebbe una durata di ' + str(end.time()), 'error')
    finally:
        return redirect(url_for("album_bp.show_songs_addable_album", album_id=album.Id))


#Route per raccogliere e mostrare tutti gli album di un artista

#Se un utente Free o Premium dovesse in qualche modo accedere a questa funzionalità, verrebbe rimandato alla home.
#Tramite due query vengono collezionati gli album pubblici e gli album premium dell'artista che accede alla pagina
#Nella pagina verrano visualizzati adeguatamente separati nelle due categorie
#Oltre all'icona e al nome dell'album, vengono visualizzati anche un bottone per eliminare e uno per modificare l'album
#In cima alla pagina un bottone da la possibilità di creare nuovi album

@album_bp.route('/show_my_albums')
@login_required
def show_my_albums():
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"])

    albums_free = session.query(Albums).filter(Albums.Artist == current_user.Email, Albums.Is_Restricted == False)
    albums_premium= session.query(Albums).filter(Albums.Artist == current_user.Email, Albums.Is_Restricted == True)
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
       
    return render_template("show_my_albums.html", user=current_user, playlists=playlists, albums_free=albums_free, albums_premium=albums_premium)



#Route per eliminare un album

#Se un utente Free o Premium dovesse in qualche modo accedere a questa funzionalità, verrebbe rimandato alla home.
#Lo stesso avviene se un artista dovesse accedere a questa funzionalità per un album non suo.
#Dopo gli opportuni controlli, viene chiamata l'opportuna funzione in Albums

@album_bp.route('/delete_album/<album_id>')
@login_required
def delete_album(album_id):
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"])
    
    album = session.query(Albums).filter(Albums.Id == album_id).first()

    if(album.Artist != current_user.Email):
        return redirect(url_for("home_bp.home"))

    Albums.delete_album(album_id, session)
    return redirect(url_for("album_bp.show_my_albums"))
    

#Route per modificare un album

#Se un utente Free o Premium dovesse in qualche modo accedere a questa funzionalità, verrebbe rimandato alla home.
#Lo stesso avviene se un artista dovesse accedere a questa funzionalità per un album non suo.
#Nel blocco try..except.., nel blocco try, vengono caricate le informazioni necessarie alla modifica dell'album,
#prese dall'apposito form
#Se tutte le informazioni sono ammesse, viene modificato l'album.
#Da notare che, nel caso in cui l'album fosse originariamente un contenuto Premium che tramite modifica viene
#declassato a contenuto pubblico, eventuali canzoni Premium vengono tolte dall'album, la cui durata si aggiorna
#di conseguenza
#Se le informazioni non sono ammesse, e questo avviene quando 1)il nome dell'album eccede i 10 ch (gestito dal form)
#                                                             2)il nome dell'album è uguale a quello di un album 
#                                                               già esistente e caricato dal medesimo artista (gestito dal blocco except)
#si resterà sulla pagina dedicata al form, che mostrerà specifici messaggi d'errore


@album_bp.route('/edit_album/<album_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def edit_album(album_id):
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"])

    try:
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        album = session.query(Albums).filter(Albums.Id == album_id).first()

        if(album.Artist != current_user.Email):
            return redirect(url_for("home_bp.home"))
        
        if album.Is_Restricted == True:
            restriction = 'Premium'
        else:
            restriction = 'Free'

        form = upload_AlbumForm(name=album.Name, releaseDate=album.ReleaseDate, recordHouse=album.Record_House, type = restriction)
        
        if form.validate_on_submit():
            name = sqlescape(form.name.data)
            recordHouse = form.recordHouse.data
            if form.type.data == 'Premium':
                restriction = True
            else:
                restriction = False
            
            at = album.Duration
            start = datetime.datetime(10,10,10, hour=at.hour, minute=at.minute, second=at.second)
            
            if(album.Is_Restricted == True and restriction==False):
                songs = session.query(Songs).filter(Songs.Id.in_(session.query(AlbumsSongs.song_id).filter(AlbumsSongs.album_id==album_id)), Songs.Is_Restricted==True)
                for s in songs:
                    st = s.Duration
                    minus = datetime.timedelta(seconds=st.second, minutes=st.minute, hours=st.hour)
                    start -= minus

                    Albums.remove_song(album, s.Id, session)
                
            Albums.update_album(album_id, name, album.ReleaseDate, recordHouse, start.time(), restriction, session)
            return redirect(url_for("album_bp.show_my_albums", user=current_user, playlists=playlists))
        return render_template("edit_album.html", user=current_user, playlists=playlists, id=album_id, form=form)

    except exc.SQLAlchemyError as err:
        session.rollback()
        flash(err.orig.diag.message_primary, 'error')   
        return render_template("edit_album.html", user=current_user, playlists=playlists, id=album_id, form=form)
    

#Route per visualizzare la pagina contenente alcune informazioni di un album, come il titolo, la durata, quanti e quali brani
#sono presenti e il numero di 'Mi piace'

#A questa pagina ha accesso chiunque
#Se l'utente visualizza la pagina inerente ad un album non suo, ha la possibilità di mettere 'Mi piace'
#Se l'utente visualizza la pagina inerente ad un album suo, ha la possibilità di accedere alla pagina per aggiungere canzoni

@album_bp.route('/show_album/<album_id>/<artist>')
@login_required
def show_album(album_id, artist):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    album = session.query(Albums).filter(Albums.Id == album_id).first()
    artist_user = session.query(Artists).filter(Artists.Email == artist).first()
    songs = session.query(Songs).filter(Songs.Id.in_(session.query(AlbumsSongs.song_id).filter(AlbumsSongs.album_id == album_id))).all()
    albums = session.query(Albums).filter(Albums.Artist == artist, Albums.Id != album_id).all()
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    n_songs = len(songs)
    
    if session.query(Users_liked_Albums).filter(Users_liked_Albums.album_id==album.Id, Users_liked_Albums.user_email==current_user.Email).first() is None:
        like = False
    else:
        like = True
    
    return render_template("show_album.html", user = current_user, album = album, songs = songs, albums = albums, n_songs = n_songs, playlists = playlists, artist_name = artist_user.Name, like = like)


#Route per rimuovere una canzone da un album

#Se un utente Free o Premium dovesse in qualche modo accedere a questa funzionalità, verrebbe rimandato alla home.
#Lo stesso avviene se un artista dovesse accedere a questa funzionalità per un album o una canzone non suoi.
#Una volta individuati la canzone e l'album tramite query, alla durata dell'album viene sottratta la durata
#della canzone, che successivamente viene rimossa dall'album

@album_bp.route('/remove_song_from_album/<song_id>/<album_id>', methods=['GET', 'POST'])
@login_required
def remove_song_from_album(song_id, album_id):
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"])

    album = session.query(Albums).filter(Albums.Id == album_id).first()
    song = session.query(Songs).filter(Songs.Id == song_id).first()

    if(album.Artist != current_user.Email or song.Artist != current_user.Email):
        return redirect(url_for("home_bp.home"))

    st = song.Duration
    at = album.Duration

    start = datetime.datetime(10, 10, 10, hour=at.hour, minute=at.minute, second=at.second)
    minus = datetime.timedelta(seconds=st.second, minutes=st.minute, hours=st.hour)
    end = start - minus

    Albums.update_album(album.Id, album.Name, album.ReleaseDate,album.Record_House, end.time(), album.Is_Restricted, session)
    Albums.remove_song(album, song_id, session)

    return redirect(url_for("album_bp.show_album", album_id=album.Id, artist=current_user.Email))


#Route per mettere 'Mi piace' ad un album

#A questa funzionalità ha accesso chiunque
#Prima di effettuare l'azione e modificare il numero di 'Mi piace' dell'album, è opportuno controllare che
#l'utente in questione non abbia già messo 'Mi piace' all'album, in modo che utenti malintenzionati
#non accedano a questa funzionalià in maniera diretta andando a pompare o sgonfiare i 'Mi piace' a loro piacimento

@album_bp.route('/add_to_liked_albums/<album_id>/<int:page>')
@login_required # richiede autenticazione
def add_to_liked_albums(album_id, page):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    album = session.query(Albums).filter(Albums.Id == album_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()

    if(session.query(Users_liked_Albums).filter(Users_liked_Albums.album_id == album_id, Users_liked_Albums.user_email==user.Email).first() is None):
        Users.add_album_to_liked(user, album, session)
        Albums.update_likes(album.N_Likes + 1, album_id, session)

    if(page == 1): #semplice controllo per sapere da che pagina ho messo 'Mi piace' ed essere reindirizzato correttamente
        return redirect(url_for("find_bp.find"))
    else:
        return redirect(url_for("album_bp.show_album", album_id=album_id, artist=album.Artist))


#Route per togliere 'Mi piace' ad un album

#A questa funzionalità ha accesso chiunque
#Prima di effettuare l'azione e modificare il numero di 'Mi piace' dell'album, è opportuno controllare che
#l'utente in questione abbia già messo 'Mi piace' all'album, in modo che utenti malintenzionati
#non accedano a questa funzionalià in maniera diretta andando a pompare o sgonfiare i 'Mi piace' a loro piacimento

@album_bp.route('/remove_from_liked_albums/<album_id>/<int:page>')
@login_required # richiede autenticazione
def remove_from_liked_albums(album_id, page):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    album = session.query(Albums).filter(Albums.Id == album_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()

    if(session.query(Users_liked_Albums).filter(Users_liked_Albums.album_id == album_id, Users_liked_Albums.user_email==user.Email).first() is not None): 
        Users.remove_album_from_liked(user, album_id, session)
        Albums.update_likes(album.N_Likes - 1, album_id, session)

    if(page == 1):
        return redirect(url_for("find_bp.find"))
    else:
        return redirect(url_for("album_bp.show_album", album_id=album_id, artist=album.Artist))