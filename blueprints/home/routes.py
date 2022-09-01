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
        
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)   
    
    liked_genres = session.query(Songs.Genre).filter(Songs.Id.in_(session.query(Users_liked_Songs.song_id).filter(Users_liked_Songs.user_email == current_user.Email))).group_by(Songs.Genre).order_by(func.count(Songs.Id).desc()).all()
    
    if (len(liked_genres) == 0):
        most_liked_songs=session.query(Songs).filter(Songs.Id.in_(session.query(Users_liked_Songs.song_id))).order_by(Songs.N_Likes.desc()).all()
        res=[]
        for i in range(10):
            if (len(most_liked_songs) > 0):
                x = most_liked_songs[0]
                res.append(x)
                most_liked_songs.remove(x)
    else:
        my_disliked_songs = session.query(Songs).filter(Songs.Id.not_in(session.query(Users_liked_Songs.song_id).filter(Users_liked_Songs.user_email == current_user.Email))).all()
        res=[]
        for x in liked_genres:
            if (len(res) < 10):
                for y in my_disliked_songs:
                    if y.Genre == x:
                        if y not in res:
                            res.append(y)
                            my_disliked_songs.remove(y)
    
    return render_template("home.html", user=current_user, playlists=playlists, consigli=res)