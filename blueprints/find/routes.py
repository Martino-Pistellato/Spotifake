from flask import Blueprint, render_template
from flask import current_app as app
from flask_login import *
from blueprints import *

# Blueprint Configuration
find_bp = Blueprint(
    'find_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

#Route per collezionare e mostare i contenuti all'interno dell'applicazione

#A questa pagina ha accesso chiunque

#In questa pagina vengono visualizzati tutti i contenuti presenti nell'applicazione,
#siano canzoni, album o artisti, ma, a seconda del tipo di profilo, vengono visualizzati contenuti diversi:
#Un utente Free avrà a sua disposizione i contenuti pubblici, oltre alle pagine degli artisti
#Un utente Premium avrà accesso ad ogni contenuto
#Un utente Artist avrà accesso ad ogni contenuto, ma non saranno visualizzati i contenuti da lui creati nè la sua pagina artista

#Dopo aver collezionato in maniera opportuna quel che va mostrato all'utente, si creano due liste, una per le canzoni
#e una per gli album, in cui vengono inserite le informazioni da mostrare per ciascun contenuto, cioè il nome, l'artista,
#la durata e se l'utente ha messo 'Mi piace' o meno per quel contenuto, così da dare la possibilità di metterlo/toglierlo
#nella pagina. Vengono inoltre inserite informazioni extra da essere passate ad altre route/pagine, 
#come l'ID del contenuto e la mail dell'artista

#I contenuti nella pagina sono mostati divisi opportunamente nei 3 gruppi Brani, Album e Artisti
#Oltre alla possibilità di metter 'Mi piace' si può cliccare sul nome di un contenuto o di un artista 
#per visualizzarne la rispettiva pagina

#Una barra di ricerca permette di navigare agevolmente fra i contenuti tramite un meccanismo show-hide:
#se, per esempio, l'utente dovesse digitare la lettera L nella barra di ricerca, solo i contenuti e gli artisti
#con tale lettera nel nome saranno visibili, mentre gli altri verranno nascosti

@find_bp.route('/find')
def find():
    if(current_user.Profile == 'Artist'):#l'artista non vede i propri contenuti
        session = Session(bind=engine["artist"])
        songs = session.query(Songs).filter(Songs.Artist != current_user.Email)
        albums = session.query(Albums).filter(Albums.Artist != current_user.Email)
        artists=session.query(Artists).filter(Artists.Email != current_user.Email)

    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
        songs = session.query(Songs)
        albums = session.query(Albums)
        artists=session.query(Artists)

    else: #l'utente Free non vede i contenuti Premium
        session = Session(bind=engine["free"])
        songs = session.query(Songs).filter(Songs.Is_Restricted == False)
        albums = session.query(Albums).filter(Albums.Is_Restricted == False)
        artists=session.query(Artists)
        
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)

    lst_s=[]
    lst_a=[]
  
    for s in songs:
        if session.query(Users_liked_Songs).filter(Users_liked_Songs.song_id==s.Id, Users_liked_Songs.user_email==current_user.Email).first() is None:
            like = False #se non ho messo 'Mi piace' ad una canzone, me ne viene data la possibilità
        else:
            like = True #se ho messo 'Mi piace', ho la possibilità di toglierlo
        artist = session.query(Artists).filter(Artists.Email == s.Artist).first()
        lst_s.append([s.Name, s.Duration, artist.Name, s.Id, like, artist.Email]) #la lista viene popolata con n-uple contenenti le informazioni necessarie 
    
    for a in albums:
        if session.query(Users_liked_Albums).filter(Users_liked_Albums.album_id==a.Id, Users_liked_Albums.user_email==current_user.Email).first() is None:
            like = False #se non ho messo 'Mi piace' ad un album, me ne viene data la possibilità
        else:
            like = True #se ho messo 'Mi piace', ho la possibilità di toglierlo
        artist = session.query(Artists).filter(Artists.Email == a.Artist).first()
        lst_a.append([a.Name, a.Duration, artist.Name, a.Id, like, artist.Email]) #la lista viene popolata con n-uple contenenti le informazioni necessarie 
      
    
    return render_template("find.html",user=current_user,playlists=playlists,albums=lst_a,songs=lst_s, artists = artists)