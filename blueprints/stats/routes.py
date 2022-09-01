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

@stats_bp.route('/stats')
def stats():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    if(current_user.Profile=='Artist'):
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
            
        my_songs=session.query(Songs).filter(Songs.Artist==current_user.Email).order_by(Songs.N_Likes.desc())
        my_albums=session.query(Albums).filter(Albums.Artist==current_user.Email).order_by(Albums.N_Likes.desc())    
        
        return render_template("stats.html", user=current_user, playlists=playlists, my_songs=my_songs, my_albums=my_albums)
    return redirect(url_for('home_bp.home'))

@stats_bp.route('/get_countries')
def get_countries():
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

@stats_bp.route('/get_ages')
def get_ages():
    
    all_liked_songs=session.query(Users_liked_Songs.song_id)
    my_liked_songs=session.query(Songs.Id).filter(and_(Songs.Artist==current_user.Email,Songs.Id.in_(all_liked_songs)))
    users_like_songs=session.query(Users.Email).filter(Users.Email.in_(session.query(Users_liked_Songs.user_email).filter(Users_liked_Songs.song_id.in_(my_liked_songs))))
        
    all_liked_albums=session.query(Users_liked_Albums.album_id)
    my_liked_albums=session.query(Albums.Id).filter(and_(Albums.Artist==current_user.Email,Albums.Id.in_(all_liked_albums)))
    users_like_albums=session.query(Users.Email).filter(Users.Email.in_(session.query(Users_liked_Albums.user_email).filter(Users_liked_Albums.album_id.in_(my_liked_albums))))
    
    users=session.query(Users).filter(or_(Users.Email.in_(users_like_songs), Users.Email.in_(users_like_albums))).all()
    
    medium_age = 0
    for x in users:
        medium_age += 2022-x.BirthDate.year
    
    if(len(users)>0):
        medium_age /= len(users)
        
    
    
    res={}
    for age in users:
        if 2022-age.BirthDate.year not in res:
            res[2022-age.BirthDate.year] = 1
        else:
            res[2022-age.BirthDate.year] += 1
    
    
    return jsonify({'dati':res})

@stats_bp.route('/get_genders')
def get_genders():
    
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