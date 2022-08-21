from flask import Blueprint, render_template, redirect, url_for, request
from flask import current_app as app
from flask_login import *
from blueprints.models import *


login_manager=LoginManager()
login_manager.init_app(app)

# Blueprint Configuration
profile_bp = Blueprint(
    'profile_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@profile_bp.route('/profile')
@login_required # richiede autenticazione
def profile():
    return render_template("profile.html", user = current_user)

@profile_bp.route('/update')
@login_required
def update():
    return render_template("update_info.html", user = current_user)

@profile_bp.route('/update_info/<string:Email>', methods=['GET', 'POST']) 
@login_required
def update_info(Email): 
    if request.method == 'POST':
        session.query(Users).filter(Users.Email == Email).update({Users.Name : request.form["name"]})
        session.commit()
        return redirect(url_for('profile_bp.profile'))