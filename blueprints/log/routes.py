from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app as app
from flask_login import *
from sqlalchemy import exc
from blueprints import *
from ..forms import subscribeForm, loginForm

login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader # attenzione a questo !
def get_user_by_email(email):
    user = session.query(Users).filter(Users.Email == email).first()
    return Users(user.Email, user.Name, user.BirthDate, user.Country, user.Gender, user.Password, user.Profile)

# Blueprint Configuration
login_bp = Blueprint(
    'login_bp', __name__,
    template_folder='templates',
   
)


@login_manager.user_loader # attenzione a questo !
def get_user_by_email(email):
    user = session.query(Users).filter(Users.Email == email).first()
    return Users(user.Email, user.Name, user.BirthDate, user.Country, user.Gender, user.Password, user.Profile)


@login_bp.route('/', methods=["GET", "POST"])
def login():
    form = loginForm()
    if form.validate_on_submit():
        email = form.email.data
        pwd = form.password.data
        
        real_user = session.query(Users).filter(Users.Email == email).first()
        if(real_user is not None and bcrypt.check_password_hash(real_user.Password, pwd)):  
            user = get_user_by_email(email)
            login_user(user) # chiamata a Flask - Login
            return redirect(url_for('home_bp.home'))    
        else:
            return render_template('login.html',form=form)
    return render_template('login.html',form=form)

@login_bp.route('/subscribe', methods=["GET", "POST"])
def subscribe():
    form = subscribeForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        encrypted_pwd = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
        profile = form.profile.data
        gender = form.gender.data
        country = form.country.data
        birthday = form.birthday.data
        if(profile=='Artist'):
            artist = Artists(email, name, birthday, country, gender, encrypted_pwd, profile)
            Artists.create_artist(artist)
        elif(profile=='Premium'):
            premium = Premium(email, name, birthday, country, gender, encrypted_pwd, profile)
            Premium.create_premium(premium)
        else:
            user = Users(email, name, birthday, country, gender, encrypted_pwd, profile)
            Users.create_user(user)
        return redirect(url_for('login_bp.login'))
    return render_template('subscribe.html',form=form)


@login_bp.route('/logout')
@login_required # richiede autenticazione
def logout():
    logout_user() # chiamata a Flask - Login
    return redirect(url_for('login_bp.login'))