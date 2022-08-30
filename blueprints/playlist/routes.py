from flask import Blueprint, render_template, redirect, url_for, request
from flask import current_app as app
from flask_login import *
from blueprints.models import *
from datetime import timedelta
import datetime
from ..forms import upload_PlaylistForm

# Blueprint Configuration
playlist_bp = Blueprint(
    'playlist_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@playlist_bp.route('/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    if(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    if(current_user.Profile == 'Free'):
        session = Session(bind=engine["free"])

    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    form = upload_PlaylistForm()
    
    if form.validate_on_submit():
        user = session.query(Users).filter(Users.Email == current_user.Email).first()
        playlist = Playlists(form.name.data)
        Playlists.create_playlist(playlist, session)
        Users.add_playlist(user, playlist, session)
        
        return redirect(url_for("playlist_bp.show_songs_addable", playlist_id=playlist.Id))
    return render_template('playlist.html', form=form, user=current_user, playlists=playlists)

@playlist_bp.route('/show_songs_addable/<playlist_id>', methods=['GET', 'POST'])
@login_required
def show_songs_addable(playlist_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
        songs = session.query(Songs).filter(Songs.Id.not_in(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==playlist_id)))
    
    if(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
        songs = session.query(Songs).filter(Songs.Id.not_in(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==playlist_id)))
    
    if(current_user.Profile == 'Free'):
        session = Session(bind=engine["free"])
        songs = session.query(Songs).filter(Songs.Id.not_in(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==playlist_id)), Songs.Is_Restricted==False)
    
    pl = session.query(Playlists).filter(Playlists.Id == playlist_id).first()
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)     
    
    return render_template("add_songs.html", songs = songs, user = current_user, playlist = pl, playlists = playlists)

@playlist_bp.route('/show_playlist_content/<playlist_id>', methods=['GET', 'POST'])
@login_required
def show_playlist_content(playlist_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    if(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    if(current_user.Profile == 'Free'):
        session = Session(bind=engine["free"])
        
    pl = session.query(Playlists).filter(Playlists.Id==playlist_id).first()
    songs = session.query(Songs).filter(Songs.Id.in_(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==pl.Id))).all
    
    #songs = session.query(PlaylistsSongs).filter(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==playlist.Id))
    
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    n_songs = len(songs)
    return render_template("show_playlist_content.html", songs = songs, user = current_user, playlist = pl, playlists = playlists, n_songs = n_songs)


@playlist_bp.route('/add_songs/<song_id>/<playlist_id>', methods=['GET', 'POST'])
@login_required
def add_songs(song_id, playlist_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    if(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    if(current_user.Profile == 'Free'):
        session = Session(bind=engine["free"])

    song = session.query(Songs).filter(Songs.Id == song_id).first()
    playlist = session.query(Playlists).filter(Playlists.Id==playlist_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()
        
    Playlists.add_song_to_playlist(playlist, song, session)

    st = song.Duration
    pt = playlist.Duration

    start = datetime.datetime(10, 10, 10, hour=pt.hour, minute=pt.minute, second=pt.second)
    add = datetime.timedelta(seconds=st.second, minutes=st.minute, hours=st.hour)
    end = start + add

    Playlists.update_playlist(playlist_id, playlist.Name, end.time(), session)
   
    return redirect(url_for("playlist_bp.show_songs_addable", playlist_id=playlist.Id))

@playlist_bp.route('/delete_playlist/<pl_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def delete_playlist(pl_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    if(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    if(current_user.Profile == 'Free'):
        session = Session(bind=engine["free"])
    
    user = session.query(Users).filter(Users.Email == current_user.Email).first()
    Playlists.delete_playlist(pl_id, session)

    return redirect(url_for("library_bp.library"))

@playlist_bp.route('/edit_playlist/<pl_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def edit_playlist(pl_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    if(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    if(current_user.Profile == 'Free'):
        session = Session(bind=engine["free"])

    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    pl = session.query(Playlists).filter(Playlists.Id == pl_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()

    form = upload_PlaylistForm(name=pl.Name)
    
    if form.validate_on_submit():
        Playlists.update_playlist(pl_id, form.name.data, pl.Duration, session)
                    
        return redirect(url_for("library_bp.library"))
        
    return render_template("edit_playlist.html", user=current_user, playlists=playlists, name=pl.Name, id=pl_id, form=form)


@playlist_bp.route('/remove_song/<song_id>/<pl_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def remove_song(song_id, pl_id):
    if(current_user.Profile == 'Artist'):
        session = Session(bind=engine["artist"])
    if(current_user.Profile == 'Premium'):
        session = Session(bind=engine["premium"])
    if(current_user.Profile == 'Free'):
        session = Session(bind=engine["free"])

    playlist = session.query(Playlists).filter(Playlists.Id == pl_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()

    Playlists.remove_song(playlist, song_id, session)
    song=session.query(Songs).filter(Songs.Id == song_id).first()

    st = song.Duration
    pt = playlist.Duration

    start = datetime.datetime(10, 10, 10, hour=pt.hour, minute=pt.minute, second=pt.second)
    minus = datetime.timedelta(seconds=st.second, minutes=st.minute, hours=st.hour)
    end = start + minus

    Playlists.update_playlist(pl_id, playlist.Name, end.time(), session)

    return redirect(url_for("playlist_bp.show_playlist_content", playlist_id = playlist.Id))