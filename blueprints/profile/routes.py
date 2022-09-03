from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask import current_app as app
from flask_login import *
from blueprints.models import *
from sqlescapy import sqlescape
from ..forms import update_profileForm

# Blueprint Configuration
profile_bp = Blueprint(
    'profile_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

#Route per visualizzare il proprio profilo

#A questa pagina ha accesso chiunque
#Questa route reindirizza alla propria pagina profilo, in cui oltre alla foto profilo (icona)
#e al proprio nome, vi sono 3 bottoni: Logout, per eseguire il logout, Modifica profilo, per cambiare il proprio nome
#e/o il tipo di account, Cancella profilo, per eliminare l'utente dal DB

@profile_bp.route('/profile')
@login_required # richiede autenticazione
def profile():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        
    return render_template("profile.html", user = current_user, playlists=playlists)

#Route per aggiornare il proprio profilo

#A questa pagina ha accesso chiunque
#Una volta caricate le informazioni necessarie ala modifica della profilo, prese dall'apposito form,
#se tutte le informazioni sono ammesse, viene modificato il profilo
#Se le informazioni non sono ammesse, e questo avviene quando 1)il nome utente eccede i 20 ch (gestito dal form)
#                                                            
#si resterà sulla pagina dedicata al form, che mostrerà specifici messaggi d'errore


@profile_bp.route('/update_info', methods=['GET', 'POST']) 
@login_required
def update_info():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    form = update_profileForm(name=current_user.Name, profile=current_user.Profile)

    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        
    if form.validate_on_submit():
        name = sqlescape(form.name.data)
        prf = form.profile.data
        
        user = session.query(Users).filter(Users.Email == current_user.Email).first()
        Users.update_user(user, name, session)
        Users.update_profile(user, prf, session)
                
        return redirect(url_for('profile_bp.profile'))
        
    return render_template("update_info.html", form=form, playlists=playlists, user=current_user)


#Route per cancellare l'utente dal DB

#A questa funzionalità ha accesso chiunque
#Una volta eseguito il logout, l'utente viene rimosso dal DB, portando alla cancellazione di ogni suo contenuto (playlist, canzoni, album, 'Mi piace')

@profile_bp.route('/delete_profile')
@login_required
def delete_profile():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    user = session.query(Users).filter(Users.Email == current_user.Email).first()
    songs_liked=session.query(Songs).filter(Songs.Id.in_(session.query(Users_liked_Songs.song_id).filter(Users_liked_Songs.user_email==user.Email))).all()
    albums_liked=session.query(Albums).filter(Albums.Id.in_(session.query(Users_liked_Albums.album_id).filter(Users_liked_Albums.user_email==user.Email))).all()
    
    for s in songs_liked:
        Songs.update_likes(s.N_Likes - 1, s.Id, session)

    for a in albums_liked:
        Albums.update_likes(a.N_Likes - 1, a.Id, session)
    
    logout_user()
    Users.delete_user(user, session)
    
    return redirect(url_for("login_bp.login"))