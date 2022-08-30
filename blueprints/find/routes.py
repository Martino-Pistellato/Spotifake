from flask import Blueprint, render_template, redirect, url_for
from flask import current_app as app
from flask_login import *
from blueprints import *

# Blueprint Configuration
find_bp = Blueprint(
    'find_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@find_bp.route('/find')
def find():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    if(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    if(current_user.Profile == 'Free'):
        session = Session(bind=engine["free"])
        
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    songs = session.query(Songs)
    albums = session.query(Albums)
    lst_s=[]
    lst_a=[]
    
    for s in songs:
        if session.query(Users_liked_Songs).filter(Users_liked_Songs.song_id==s.Id, Users_liked_Songs.user_email==current_user.Email).first() is None:
            like = False
        else:
            like = True
        artist = session.query(Users).filter(Users.Email == s.Artist).first()
        lst_s.append([s.Name, s.Duration, artist.Name, s.Id, like])   
    
    for a in albums:
        if session.query(Users_liked_Albums).filter(Users_liked_Albums.album_id==a.Id, Users_liked_Albums.user_email==current_user.Email).first() is None:
            like = False
        else:
            like = True
        artist = session.query(Users).filter(Users.Email == a.Artist).first()
        lst_a.append([a.Name, a.Duration, artist.Name, a.Id, like, artist.Email])   
    
    return render_template("find.html",user=current_user,playlists=playlists,albums=lst_a,songs=lst_s)