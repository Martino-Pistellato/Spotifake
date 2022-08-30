from flask import Blueprint, render_template, redirect, url_for, request
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
    if current_user.Profile == 'Artist':
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        
        my_songs=session.query(Songs).filter(Songs.Artist==current_user.Email).order_by(Songs.N_Likes.desc())
        my_albums=session.query(Albums).filter(Albums.Artist==current_user.Email).order_by(Albums.N_Likes.desc())
        
        all_liked_songs=session.query(Users_liked_Songs.song_id)
        my_liked_songs=session.query(Songs).filter(and_(Songs.Artist==current_user.Email,Songs.Id.in_(all_liked_song.Id)))
        users_like_songs=session.query(Users).filter(Users.Email.in_(session.query(Users_liked_Songs.user_email).filter(Users_liked_Songs.song_id.in_(my_liked_songs.Id))))
        
        all_liked_albums=session.query(Users_liked_Albums.album_id)
        my_liked_albums=session.query(Album).filter(and_(Albums.Artist==current_user.Email,Album.Id.in_(all_liked_albums.Id)))
        users_like_albums=session.query(Users).filter(Users.Email.in_(session.query(Users_liked_Albums.user_email).filter(Users_liked_Albums.album_id.in_(my_liked_albums.Id))))
        
        users_like_me=session.query(Users).filter(Users.Email.in_(or_(users_like_songs.Email,users_like_albums.Email))).all()
        
        medium_age = 0
        for x in users_like_me:
            medium_age += 2022-x.BirthDate.year
        medium_age /= len(users_like_me)    
        
        countries = session.query(users_like_me.Country,func.count(users_like_me.Email)).group_by(users_like_me.Country)
        
        return render_template("stats.html", user=current_user, playlists=playlists, users=users_like_me, my_songs=my_songs, my_albums=my_albums, countries=countries)
    return redirect(url_for('home_bp.home'))