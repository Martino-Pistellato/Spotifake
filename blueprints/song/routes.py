from flask import Blueprint, render_template, redirect, url_for
from flask_login import *
from blueprints.models import *
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
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    if (current_user.Profile == 'Artist'):
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
                Songs.create_song(song)
                user = session.query(Users).filter(Users.Email == current_user.Email).first()
                Users.add_song_if_artist(user, song)
                
                return redirect(url_for("song_bp.show_my_songs", user=current_user, playlists=playlists))    
            return render_template('upload_song.html',form=form, user=current_user, playlists=playlists)
        except exc.SQLAlchemyError as err:
            session.rollback()
            return render_template('upload_song.html',form=form, user=current_user, playlists=playlists)
    return redirect(url_for("home_bp.home"))

@song_bp.route('/edit_song/<song_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def edit_song(song_id):
    if (current_user.Profile == 'Artist'):
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
                
                Songs.update_song(song_id, name, time, genre, restriction)
                
                return redirect(url_for("song_bp.show_my_songs", user=current_user, playlists=playlists)) 
            
            return render_template("edit_song.html", user=current_user, playlists=playlists, id=song_id, form=form)
        except exc.SQLAlchemyError as err:
            session.rollback()
            return render_template("edit_song.html", user=current_user, playlists=playlists, id=song_id, form=form)
            
    return redirect(url_for("home_bp.home"))

@song_bp.route('/delete_song/<song_id>', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def delete_song(song_id):
    if (current_user.Profile == 'Artist'):
        Songs.delete_song(song_id)
        return redirect(url_for("song_bp.show_my_songs"))
    return redirect(url_for("home_bp.home"))

@song_bp.route('/show_my_songs')
@login_required # richiede autenticazione
def show_my_songs():
    if (current_user.Profile == 'Artist'):
        songs = session.query(Songs).filter(Songs.Artist == current_user.Email)
        playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
    
        return render_template("show_my_songs.html", songs = songs, user = current_user, playlists = playlists)
    return redirect(url_for("home_bp.home"))

@song_bp.route('/add_to_liked_songs/<song_id>')
@login_required # richiede autenticazione
def add_to_liked_songs(song_id):
    song = session.query(Songs).filter(Songs.Id == song_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()

    Users.add_song_to_liked(user, song)
    Songs.update_likes(song.N_Likes + 1, song_id)

    return redirect(url_for("find_bp.find"))

@song_bp.route('/remove_from_liked_songs/<song_id>')
@login_required # richiede autenticazione
def remove_from_liked_songs(song_id):
    song = session.query(Songs).filter(Songs.Id == song_id).first()
    user = session.query(Users).filter(Users.Email == current_user.Email).first()

    Users.remove_song_from_liked(user, song_id)
    Songs.update_likes(song.N_Likes - 1, song_id)

    return redirect(url_for("find_bp.find"))

