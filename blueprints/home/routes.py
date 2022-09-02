from flask import Blueprint, render_template, redirect, url_for, flash
from flask import current_app as app
from flask_login import *
from blueprints import *
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

login_manager=LoginManager()
login_manager.init_app(app)

# Blueprint Configuration
home_bp = Blueprint(
    'home_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

#Route per visualizzare la home

#A questa pagina ha accesso chiunque
#Questa è la prima pagina a venire visualizzata dopo il login
#Oltre alle playlist dell'utente, vengono visualizzate 5 canzoni "consigliate"
#L'algoritmo, implementato in questa route, funziona così:
#Tramite una prima query vengono collezionate le canzoni a cui l'utente ha messo 'Mi piace', e tramite una seconda query
#basata sulla prima vengono estratti i generi di tali canzoni, ordinati in ordine decrescente in base a quante canzoni 
#fra le piaciute hanno quel genere
#Vengono poi collezionate le canzoni a cui l'utente non ha messo 'Mi piace', in ordine decrescente per numero di 'Mi piace, 
#facendo sempre attenzione al tipo di profilo:
#A un utente Free non vengono consigliate canzoni Premium
#Fra i consigliati di un artista non possono di certo esserci le su stesse canzoni
#Una volta collezionate queste informazioni adeguatamente, viene creata una lista in cui inserire i 5 brani consigliati
#Come prima cosa si passano in rassegna i generi piaciuti: se fra le canzoni senza 'Mi piace' da parte dell'utente
#ci sono canzoni aventi come genere un genere piaciuto, queste vengono inserite nella lista.
#Se alla fine c'è ancora posto nella lista, vengono inserite le canzoni con il numero
#di 'Mi piace' più alto fra le rimanenti senza 'Mi piace' da parte dell'utente
#In cima alla pagina viene visualizzato anche un bottone per creare una nuova playlist

@home_bp.route('/home')
@login_required # richiede autenticazione
def home():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
        songs = session.query(Songs).filter(Songs.Artist == current_user.Email).all() 
        albums = session.query(Albums).filter(Albums.Artist == current_user.Email).all() 
        if(len(songs) == len(albums) == 0):
            if(date.today().day - current_user.SubscribedDate.day) >= 5 or (date.today().month - current_user.SubscribedDate.month) > 0:
                user = session.query(Artists).filter(Artists.Email == current_user.Email).first()
                Users.update_profile(user, 'Free')
                flash('Il tuo profilo è stato declassato a causa della tua inattività', 'error')
                return redirect(url_for('home_bp.home'))

        albums=session.query(Albums).filter(Albums.Duration == '00:00:00')
        for a in albums:
            if (date.today().day - a.ReleaseDate.day) >=3 or (date.today().month - a.ReleaseDate.month) > 0 :
                Albums.delete_album(a.Id, session)
                flash("L'album "+str(a.Name)+" è stato cancellato a causa della sua inattività",'error')

    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])   
    
    #prendo le canzoni piaciute e i generi di tali canzoni
    liked_songs = session.query(Songs.Id).filter(Songs.Id.in_(session.query(Users_liked_Songs.song_id).filter(Users_liked_Songs.user_email==current_user.Email)))
    liked_genres = session.query(Songs.Genre).filter(Songs.Id.in_(liked_songs)).group_by(Songs.Genre).order_by(func.count(Songs.Id).desc()).all()
    
    #per facilitare/permettere i controlli nei cicli for sottostanti
    liked_genres_str = [x[0] for x in liked_genres]

    #colleziono le canzoni potenzialmente interessanti, facendo attenzione al profilo dell'utente
    if (current_user.Profile == "Free"):
        not_liked_songs = session.query(Songs).filter(and_(Songs.Is_Restricted==False,Songs.Id.not_in(liked_songs))).order_by(Songs.N_Likes.desc()).all()
    elif(current_user.Profile == "Artist"):
        not_liked_songs = session.query(Songs).filter(and_(Songs.Artist != current_user.Email,Songs.Id.not_in(liked_songs))).order_by(Songs.N_Likes.desc()).all()
    else:
        not_liked_songs = session.query(Songs).filter(Songs.Id.not_in(liked_songs)).order_by(Songs.N_Likes.desc()).all()
        
    res=[]
    for lg in liked_genres_str: #scorro i generi piaciuti
            for nls in not_liked_songs: #scorro le canzoni senza 'Mi piace' da parte dell'utente
                if (len(res) < 5):
                    if  nls.Genre == lg: #se la canzone ha lo stesso genere di un genere piaciuto
                        res.append(nls) #aggiungo la canzone alle consigliate
                        not_liked_songs.remove(nls) #la rimuovo da wuelle senza 'Mi piace'
        
    
    if(len(res) < 5 ): #se c'è ancora spazio nella lista
        for i in range(len(res), 5): 
            if (len(not_liked_songs) > 0): #se ci sono ancora canzoni fra quelle senza 'Mi piace'
                nls = not_liked_songs[0]
                res.append(nls) #inserisco la testa della lista, che avrà il numero di 'Mi piace' più alto fra le restanti
                not_liked_songs.remove(nls)#la rimuovo dalle canzoni senza 'Mi piace'
                
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    return render_template("home.html", user=current_user, playlists=playlists, consigli=res)