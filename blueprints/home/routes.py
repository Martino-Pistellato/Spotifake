from flask import Blueprint, render_template, redirect, url_for
from flask import current_app as app
from flask_login import *
from blueprints import *

login_manager=LoginManager()
login_manager.init_app(app)

# Blueprint Configuration
home_bp = Blueprint(
    'home_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@home_bp.route('/home')
@login_required # richiede autenticazione
def home():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])   
    
    liked_songs = session.query(Songs.Id).filter(Songs.Id.in_(session.query(Users_liked_Songs.song_id).filter(Users_liked_Songs.user_email==current_user.Email)))
    liked_genres = session.query(Songs.Genre).filter(Songs.Id.in_(liked_songs)).group_by(Songs.Genre).order_by(func.count(Songs.Id).desc()).all()
    
    liked_genres_str = [x[0] for x in liked_genres]

    if (current_user.Profile == "Free"):
        not_liked_songs = session.query(Songs).filter(and_(Songs.Is_Restricted==False,Songs.Id.not_in(liked_songs))).order_by(Songs.N_Likes.desc()).all()
    elif(current_user.Profile == "Artist"):
        not_liked_songs = session.query(Songs).filter(and_(Songs.Artist != current_user.Email,Songs.Id.not_in(liked_songs))).order_by(Songs.N_Likes.desc()).all()
    else:
        not_liked_songs = session.query(Songs).filter(Songs.Id.not_in(liked_songs)).order_by(Songs.N_Likes.desc()).all()
        
    res=[]
    for lg in liked_genres_str:
        if (len(res) < 5):
            for nls in not_liked_songs:
                if  nls.Genre == lg:
                    res.append(nls)
                    not_liked_songs.remove(nls)
    
    
    if(len(res) < 5 ):
        for i in range(len(res), 5):
            if (len(not_liked_songs) > 0):
                nls = not_liked_songs[0]
                res.append(nls)
                not_liked_songs.remove(nls)
                
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    return render_template("home.html", user=current_user, playlists=playlists, consigli=res)