from flask import Blueprint, render_template, redirect, url_for, request
from flask import current_app as app
from flask_login import *
from blueprints.models import *

# Blueprint Configuration
library_bp = Blueprint(
    'library_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@library_bp.route('/library')
@login_required
def library():
    playlists = session.query(Playlists).filter(Playlists.Id.in_(session.query(PlaylistsUsers.playlist_id).filter(PlaylistsUsers.user_email==current_user.Email)))
    return render_template("library.html", playlists=playlists, user=current_user)
    
@library_bp.route('/albums/<user>/<playlists>')
@login_required
def library(user, playlists):
    #albums = session.query(Albums).filter(Albums.Id.in_()) -- è possibile avere degli album salvati?
    return render_template("albums.html", playlists=playlists, user=user)

@library_bp.route('/artists/<user>/<playlists>')
@login_required
def library(user, playlists):
    #artists = session.query(Users).filter(Users.Email.in_()) -- è possibile avere degli artisti salvati?
    return render_template("artists.html", playlists=playlists, user=user)
    
@library_bp.route('/songs/<user>/<playlists>')
@login_required
def library(user, playlists):
    #songs = session.query(Songs).filter(Songs.Id.in_()) -- è possibile avere delle canzoni salvate?
    return render_template("songs.html", playlists=playlists, user=user)