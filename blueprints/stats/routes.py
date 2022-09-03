from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask import current_app as app
from flask_login import *
from blueprints.models import *
from datetime import *


# Blueprint Configuration
stats_bp = Blueprint(
    'stats_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

#Route per accedere alle statistiche

#Se un utente Free o Premium dovesse accedere a questa funzionalità verrebbe rimandato alla home
#Vengono collezionate le canzoni e gli album dell'utente così da poter mostare i titoli e il numero di 'Mi piace'

@stats_bp.route('/stats')
@login_required
def stats():
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"]) 

    
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
            
    my_songs=session.query(Songs).filter(Songs.Artist==current_user.Email).order_by(Songs.N_Likes.desc())
    my_albums=session.query(Albums).filter(Albums.Artist==current_user.Email).order_by(Albums.N_Likes.desc())    
        
    return render_template("stats.html", user=current_user, playlists=playlists, my_songs=my_songs, my_albums=my_albums)

#Route per collezionare dati sui paesi

#Se un utente Free o Premium dovesse accedere a questa funzionalità verrebbe rimandato alla home
#Con una prima query vengono collezionate tutti gli ID di canzoni piaciute (in generale)
#Con una seconda query basata sulla prima si trovano gli ID delle canzoni piaciute e pubblicate dall'utente
#Con una terza, basata sulla seconda, si collezionano gli utenti che hanno messo 'Mi piace' a canzoni dell'utente
#Le stesse tre query sono poi rielaborate per ottenere gli stessi dati per quanto riguarda gli album dell'utente

#Con la query finale si collezionano i paesi ed il numero di utenti che vi vivono fra quelli che hanno messo 'Mi piace' a
#qualche contenuto dell'artista

#Viene creato un dizionario in cui la chiave è il paese e il valore è il numero di utenti
#Nella pagina i dati estratti da questo dizionario vengono mostrati sottoforma di grafico a torta, realizzato tramite AJAX,
#Javascript e Googlechart

@stats_bp.route('/get_countries')
@login_required
def get_countries():
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"])

    all_liked_songs=session.query(Users_liked_Songs.song_id)
    my_liked_songs=session.query(Songs.Id).filter(and_(Songs.Artist==current_user.Email,Songs.Id.in_(all_liked_songs)))
    users_like_songs=session.query(Users.Email).filter(Users.Email.in_(session.query(Users_liked_Songs.user_email).filter(Users_liked_Songs.song_id.in_(my_liked_songs))))
        
    all_liked_albums=session.query(Users_liked_Albums.album_id)
    my_liked_albums=session.query(Albums.Id).filter(and_(Albums.Artist==current_user.Email,Albums.Id.in_(all_liked_albums)))
    users_like_albums=session.query(Users.Email).filter(Users.Email.in_(session.query(Users_liked_Albums.user_email).filter(Users_liked_Albums.album_id.in_(my_liked_albums))))
    
    countries=session.query(Users.Country, func.count(Users.Email)).filter(or_(Users.Email.in_(users_like_songs), Users.Email.in_(users_like_albums))).group_by(Users.Country).all()
    
    res={}
    for c in countries:
        res[c[0]] = c[1]
    
    return jsonify({'dati':res})


#Route per collezionare dati sull'età

#Se un utente Free o Premium dovesse accedere a questa funzionalità verrebbe rimandato alla home
#Con una prima query vengono collezionate tutti gli ID di canzoni piaciute (in generale)
#Con una seconda query basata sulla prima si trovano gli ID delle canzoni piaciute e pubblicate dall'utente
#Con una terza, basata sulla seconda, si collezionano gli utenti che hanno messo 'Mi piace' a canzoni dell'utente
#Le stesse tre query sono poi rielaborate per ottenere gli stessi dati per quanto riguarda gli album dell'utente

#Con la query finale si collezionano gli utenti che hanno messo 'Mi piace' a qualche contenuto dell'artista 
#(N.B.: se un utente ha messo 'Mi piace' sia ad una canzone che ad un album, verrà contato una volta)

#Viene creato un dizionario in cui la chiave è l'età dell'utente che ha messo 'Mi piace' 
#e il valore è il numero di utenti con quell'età
#Nella pagina i dati estratti da questo dizionario vengono mostrati sottoforma di grafico a torta, realizzato tramite AJAX,
#Javascript e Googlechart

@stats_bp.route('/get_ages')
@login_required
def get_ages():
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"])
    
    all_liked_songs=session.query(Users_liked_Songs.song_id)
    my_liked_songs=session.query(Songs.Id).filter(and_(Songs.Artist==current_user.Email,Songs.Id.in_(all_liked_songs)))
    users_like_songs=session.query(Users.Email).filter(Users.Email.in_(session.query(Users_liked_Songs.user_email).filter(Users_liked_Songs.song_id.in_(my_liked_songs))))
        
    all_liked_albums=session.query(Users_liked_Albums.album_id)
    my_liked_albums=session.query(Albums.Id).filter(and_(Albums.Artist==current_user.Email,Albums.Id.in_(all_liked_albums)))
    users_like_albums=session.query(Users.Email).filter(Users.Email.in_(session.query(Users_liked_Albums.user_email).filter(Users_liked_Albums.album_id.in_(my_liked_albums))))
    
    users=session.query(Users).filter(or_(Users.Email.in_(users_like_songs), Users.Email.in_(users_like_albums))).all()
    
    res={}
    for age in users:
        if 2022 - age.BirthDate.year not in res:
            res[2022 - age.BirthDate.year] = 1
        else:
            res[2022 - age.BirthDate.year] += 1
    
    
    return jsonify({'dati':res})



#Route per collezionare dati sul sesso

#Se un utente Free o Premium dovesse accedere a questa funzionalità verrebbe rimandato alla home
#Con una prima query vengono collezionate tutti gli ID di canzoni piaciute (in generale)
#Con una seconda query basata sulla prima si trovano gli ID delle canzoni piaciute e pubblicate dall'utente
#Con una terza, basata sulla seconda, si collezionano gli utenti che hanno messo 'Mi piace' a canzoni dell'utente
#Le stesse tre query sono poi rielaborate per ottenere gli stessi dati per quanto riguarda gli album dell'utente

#Con la query finale si collezionano i sessi ed il numero di utenti con quel sesso fra quelli che hanno messo 'Mi piace' a
#qualche contenuto dell'artista

#Viene creato un dizionario in cui la chiave è il sesso e il valore è il numero di utenti di quel sesso
#Nella pagina i dati estratti da questo dizionario vengono mostrati sottoforma di grafico a torta, realizzato tramite AJAX,
#Javascript e Googlechart

@stats_bp.route('/get_genders')
@login_required
def get_genders():
    if(current_user.Profile != 'Artist'):
        return redirect(url_for("home_bp.home"))
    else:
        session = Session(bind=engine["artist"])
    
    all_liked_songs=session.query(Users_liked_Songs.song_id)
    my_liked_songs=session.query(Songs.Id).filter(and_(Songs.Artist==current_user.Email,Songs.Id.in_(all_liked_songs)))
    users_like_songs=session.query(Users.Email).filter(Users.Email.in_(session.query(Users_liked_Songs.user_email).filter(Users_liked_Songs.song_id.in_(my_liked_songs))))
        
    all_liked_albums=session.query(Users_liked_Albums.album_id)
    my_liked_albums=session.query(Albums.Id).filter(and_(Albums.Artist==current_user.Email,Albums.Id.in_(all_liked_albums)))
    users_like_albums=session.query(Users.Email).filter(Users.Email.in_(session.query(Users_liked_Albums.user_email).filter(Users_liked_Albums.album_id.in_(my_liked_albums))))
    
    users_gender=session.query(Users.Gender, func.count(Users.Email)).filter(or_(Users.Email.in_(users_like_songs), Users.Email.in_(users_like_albums))).group_by(Users.Gender).all()
    
    res={}
    for gen in users_gender:
        res[gen[0]] = gen[1]
    
    return jsonify({'dati':res})