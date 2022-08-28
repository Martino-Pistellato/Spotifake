from flask import Blueprint, render_template, redirect, url_for, request
from flask import current_app as app
from flask_login import *
from blueprints.models import *

# Blueprint Configuration
profile_bp = Blueprint(
    'profile_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@profile_bp.route('/profile')
@login_required # richiede autenticazione
def profile():
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        
    return render_template("profile.html", user = current_user, playlists=playlists)

@profile_bp.route('/update')
@login_required
def update():
    playlists = session.query(Playlists).filter(Playlists.User == current_user.Email)
        
    return render_template("update_info.html", user = current_user, playlists=playlists)

@profile_bp.route('/update_info/<Email>', methods=['GET', 'POST']) 
@login_required
def update_info(Email): 
    if request.method == 'POST':
        name = request.form["name"]
        if(name is not None):
            Users.update_user(Email, name)
            return redirect(url_for('profile_bp.profile'))
    return redirect(url_for("profile_bp.update"))

@profile_bp.route('/delete_profile')
@login_required
def delete_profile():
    email = current_user.Email
    logout_user()
    Users.delete_user(email)
    return redirect(url_for("login_bp.login"))