from re import template
from flask import Blueprint, render_template, redirect, url_for
from flask_login import *
from blueprints.models import *
import datetime
from ..forms import upload_SongForm

# Blueprint Configuration
song_bp = Blueprint(
    'song_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@song_bp.route('/upload_song', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def upload_song():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    
    form = upload_SongForm()
    try:
        if form.validate_on_submit():
            name = form.name.data
            time = form.time.data
            genre = form.genre.data
            if form.type.data == 'Premium':
                restriction = True
            else:
                restriction = False  
            song = Songs(name, time, genre, restriction, current_user.Email)
            user = session.query(Users).filter(Users.Email == current_user.Email).first()
            Songs.create_song(song, session)
            Users.add_song_if_artist(user, song, session)
                
            return redirect(url_for("song_bp.show_my_songs", user=current_user, playlists=playlists))    
        return render_template('upload_song.html',form=form, user=current_user, playlists=playlists)
    except exc.SQLAlchemyError as err:
        session.rollback()
        return render_template('upload_song.html',form=form, user=current_user, playlists=playlists)
    
@song_bp.route('/edit_song/<song_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def edit_song(song_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    song = session.query(Songs).filter(Songs.Id == song_id).first()
           
    if song.Is_Restricted == True:
        restriction = 'Premium'
    else:
        restriction = 'Free'
    form = upload_SongForm(name=song.Name, time=song.Duration, genre=song.Genre, type = restriction)
        
    try:
        if form.validate_on_submit():
            name = form.name.data
            time = form.time.data
            genre = form.genre.data
            if form.type.data == 'Premium':
                restriction = True
            else:
                restriction = False  
                
            Songs.update_song(song_id, name, time, genre, restriction, session)
                
            return redirect(url_for("song_bp.show_my_songs", user=current_user, playlists=playlists)) 
            
        return render_template("edit_song.html", user=current_user, playlists=playlists, id=song_id, form=form)
    except exc.SQLAlchemyError as err:
        session.rollback()
        return render_template("edit_song.html", user=current_user, playlists=playlists, id=song_id, form=form)
            
    
@song_bp.route('/delete_song/<song_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def delete_song(song_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    albums = session.query(Albums).filter(Albums.Id.in_(session.query(AlbumsSongs.album_id).filter(AlbumsSongs.song_id==song_id)))
    playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsSongs.playlist_id).filter(PlaylistsSongs.song_id==song_id)))
    song=session.query(Songs).filter(Songs.Id == song_id).first()
            
    st = song.Duration
    minus = datetime.timedelta(seconds=st.second, minutes=st.minute, hours=st.hour)
    date = datetime.date(10, 10, 10)
        
    for a in albums:
        start=datetime.datetime.combine(date, a.Duration)
        end = start - minus
        Albums.update_album(a.Id, a.Name, a.ReleaseDate, a.Record_House, end.time(), a.Is_Restricted, session)

    for p in playlists:
        start=datetime.datetime.combine(date, p.Duration)
        end = start - minus
        Playlists.update_playlist(p.Id, p.Name, end.time(), session)

    Songs.delete_song(song_id, session)
    return redirect(url_for("song_bp.show_my_songs"))
    
@song_bp.route('/show_my_songs')
@login_required # richiede autenticazione
def show_my_songs():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    songs = session.query(Songs).filter(Songs.Artist == current_user.Email)
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    
    return render_template("show_my_songs.html", songs = songs, user = current_user, playlists = playlists)
    
@song_bp.route('/add_to_liked_songs/<song_id>')
@login_required # richiede autenticazione
def add_to_liked_songs(song_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    song = session.query(Songs).filter(Songs.Id == song_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()

    Users.add_song_to_liked(user, song, session)
    Songs.update_likes(song.N_Likes + 1, song_id, session)

    return redirect(url_for("find_bp.find"))

@song_bp.route('/remove_from_liked_songs/<song_id>')
@login_required # richiede autenticazione
def remove_from_liked_songs(song_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])
        
    song = session.query(Songs).filter(Songs.Id == song_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()

    Users.remove_song_from_liked(user, song_id, session)
    Songs.update_likes(song.N_Likes - 1, song_id, session)

    return redirect(url_for("find_bp.find"))

@song_bp.route('/show_song/<song_id>')
@login_required # richiede autenticazione
def show_song(song_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    elif(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    else:
        session = Session(bind=engine["free"])

    song = session.query(Songs).filter(Songs.Id==song_id)
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    
    if session.query(Users_liked_Songs).filter(Users_liked_Songs.song_id==song.Id, Users_liked_Songs.user_email==current_user.Email).first() is None:
        like = False
    else:
        like = True
    artist = session.query(Users).filter(Users.Email==song.Artist)
    
    return render_template('show_song.html', user=current_user, playlists=playlists, song=song, artist_name=artist.Name, like=like)