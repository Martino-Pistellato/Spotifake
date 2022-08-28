from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app as app
from blueprints.models import *
from flask_login import *
from ..forms import upload_AlbumForm
import time
from datetime import timedelta
import datetime


# Blueprint Configuration
album_bp = Blueprint(
    'album_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@album_bp.route('/album')
@login_required
def album():
    if(current_user.Profile == 'Artist'):
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)        
        return render_template("create_album.html", user=current_user, playlists=playlists)

@album_bp.route('/create_album', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def create_album():
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    if (current_user.Profile == 'Artist'):
        form = upload_AlbumForm()
        form.recordHouse.choices = [(rh.Name) for rh in session.query(Record_Houses)]
        
        if form.validate_on_submit():
            name = form.name.data
            date = form.releaseDate.data
            rec_h = form.recordHouse.data
            if form.type.data == 'Premium':
                restriction = True
            else:
                restriction = False
                
            album = Albums(name, date, rec_h, current_user.Email, restriction)
            Albums.create_album(album)
            user = session.query(Users).filter(Users.Email == current_user.Email).first()
            Users.add_album_if_artist(user, album)
            
            return redirect(url_for("album_bp.show_songs_addable_album", album_name = name))    
        return render_template('create_album.html',form=form, user=current_user, playlists=playlists)
    return redirect(url_for("home_bp.home"))

@album_bp.route('/show_songs_addable_album/<album_name>', methods=['GET', 'POST'])
@login_required
def show_songs_addable_album(album_name):
    if(current_user.Profile == 'Artist'):
        album = session.query(Albums).filter(and_(Albums.Name == album_name, Albums.Artist == current_user.Email)).first()
        all_my_songs = session.query(Songs.Id).filter(Songs.Artist == current_user.Email)
        my_songs_in_album = session.query(Songs.Id).filter(Songs.Id.in_(session.query(AlbumsSongs.song_id).filter(AlbumsSongs.album_id == album.Id)))
        my_songs = session.query(Songs).filter(Songs.Id.not_in(my_songs_in_album), Songs.Id.in_(all_my_songs), Songs.Is_Restricted == False)
        if(album.Is_Restricted == True):
            my_songs = session.query(Songs).filter(Songs.Id.not_in(my_songs_in_album), Songs.Id.in_(all_my_songs))
       
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        
        return render_template("show_songs_album.html", album=album_name, user=current_user, playlists=playlists, songs=my_songs)


@album_bp.route('/add_songs_to_album/<song_id>/<album_name>', methods=['GET', 'POST'])
@login_required
def add_songs_to_album(song_id, album_name):
    if(current_user.Profile == 'Artist'):
        song = session.query(Songs).filter(Songs.Id == song_id).first()
        album = session.query(Albums).filter(Albums.Name == album_name).first()
        Albums.add_song_to_album(album, song)
        st = song.Duration
        at = album.Duration
        
        #x = 0
        #x = (at.hour + st.hour)*3600
        #x += (at.minute + st.minute)*60
        #x += at.second + st.second
        #time.strftime('%H:%M:%S', time.gmtime(x))

        start = datetime.datetime(1, 1, 1, hour=at.hour, minute=at.minute, second=at.second)
        add = datetime.timedelta(seconds=st.second, minutes=st.minute, hours=st.hour)
        end = start + add
     
        Albums.update_album(album.Id, album.Name, album.ReleaseDate,album.Record_House, end.time(), album.Is_Restricted)

        return redirect(url_for("album_bp.show_songs_addable_album", album_name=album_name))

@album_bp.route('/show_my_albums')
@login_required
def show_my_albums():
    if(current_user.Profile == 'Artist'):
       albums = session.query(Albums).filter(Albums.Artist == current_user.Email)
       playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
       
       return render_template("show_my_albums.html", user=current_user, playlists=playlists, albums=albums)

@album_bp.route('/delete_album/<album_id>')
@login_required
def delete_album(album_id):
    if (current_user.Profile == 'Artist'):
        Albums.delete_album(album_id)
        return redirect(url_for("album_bp.show_my_albums"))
    return redirect(url_for("home_bp.home"))

@album_bp.route('/edit_album/<album_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def edit_album(album_id):
    if (current_user.Profile == 'Artist'):
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        album = session.query(Albums).filter(Albums.Id == album_id).first()
        if album.Is_Restricted == True:
            restriction = 'Premium'
        else:
            restriction = 'Free'

        form = upload_AlbumForm(name=album.Name, releaseDate=album.ReleaseDate, recordHouse=album.Record_House, type = restriction)
        form.recordHouse.choices = [(rh.Name) for rh in session.query(Record_Houses)]

        if form.validate_on_submit():
            name = form.name.data
            releaseDate = form.releaseDate.data
            recordHouse = form.recordHouse.data
            if form.type.data == 'Premium':
                restriction = True
            else:
                restriction = False
            
            Albums.update_album(album_id, name, releaseDate, recordHouse, album.Duration, restriction)
            
            return redirect(url_for("album_bp.show_my_albums", user=current_user, playlists=playlists)) 
        
        return render_template("edit_album.html", user=current_user, playlists=playlists, id=album_id, form=form)
    return redirect(url_for("home_bp.home"))


@album_bp.route('/show_album/<album_name>/<artist>')
@login_required
def show_album(album_name, artist):
    album = session.query(Albums).filter(Albums.Name == album_name, Albums.Artist == artist).first()
    artist_user = session.query(Users).filter(Users.Email == artist).first()
    songs = session.query(Songs).filter(Songs.Id.in_(session.query(AlbumsSongs.song_id).filter(AlbumsSongs.album_id == album.Id))).all()
    albums = session.query(Albums).filter(Albums.Artist == artist, Albums.Id != album.Id).all()
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    n_songs = len(songs)
    
    return render_template("show_album.html", user = current_user, album = album, songs = songs, albums = albums, n_songs = n_songs, playlists = playlists, artist_name = artist_user.Name)

@album_bp.route('/remove_song_from_album/<song_id>/<album_name>', methods=['GET', 'POST'])
@login_required
def remove_song_from_album(song_id, album_name):
    if(current_user.Profile == 'Artist'):
        album = session.query(Albums).filter(Albums.Name == album_name, Albums.Artist == current_user.Email).first()
        song = session.query(Songs).filter(Songs.Id == song_id).first()
        st = song.Duration
        at = album.Duration

        start = datetime.datetime(1, 1, 1, hour=at.hour, minute=at.minute, second=at.second)
        minus = datetime.timedelta(seconds=st.second, minutes=st.minute, hours=st.hour)
        end = start - minus

        Albums.remove_song(album, song_id)

        Albums.update_album(album.Id, album.Name, album.ReleaseDate,album.Record_House, end.time(), album.Is_Restricted)


    return redirect(url_for("album_bp.show_album", album_name=album.Name, artist=current_user.Email))

@album_bp.route('/add_to_liked_albums/<album_id>')
@login_required # richiede autenticazione
def add_to_liked_albums(album_id):
    album = session.query(Albums).filter(Albums.Id == album_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()

    Users.add_album_to_liked(user, album)
    Albums.update_likes(album.N_Likes + 1, album_id)

    return redirect(url_for("find_bp.find"))

@album_bp.route('/remove_from_liked_albums/<album_id>')
@login_required # richiede autenticazione
def remove_from_liked_albums(album_id):
    album = session.query(Albums).filter(Albums.Id == album_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()

    Users.remove_album_from_liked(user, album_id)
    Albums.update_likes(album.N_Likes - 1, album_id)

    return redirect(url_for("find_bp.find"))