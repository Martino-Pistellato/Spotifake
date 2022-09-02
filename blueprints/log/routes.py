from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import current_app as app
from flask_login import *
from sqlalchemy import exc
from blueprints import *
from ..forms import subscribeForm, loginForm
from sqlescapy import sqlescape

login_manager=LoginManager()
login_manager.init_app(app)

# Blueprint Configuration
login_bp = Blueprint(
    'login_bp', __name__,
    template_folder='templates',
   
)

#Funzione per mantenere l'utente loggato una volta autenticato
@login_manager.user_loader # attenzione a questo !
def get_user_by_email(email):
    user = session.query(Users).filter(Users.Email == email).first()
    return Users(user.Email, user.Name, user.BirthDate, user.Country, user.Gender, user.Password, user.Profile, user.SubscribedDate)


#Route per effettuare il login

#A questa pagina ha accesso chiunque, essendo fra l'altro la prima pagina ad essere vista all'avvio
#dell'applicazione
#Tramite un form l'utente inserisce le sue credenziali, l'indirizzo email e la password
#Tramite una query si prende dal DB l'utente avente l'indirizzo email inserito nel form
#Se l'indirizzo è associato ad un utente esistente e la password inserita è uguale alla password (opportunamente decriptata)
#associata all'indirizzo email, l'utente viene loggato e reindirizzato alla home.
#Altrimenti l'utente resterà nella pagina di login
@login_bp.route('/', methods=["GET", "POST"])
def login():
    form = loginForm()
    if form.validate_on_submit():
        email = sqlescape(form.email.data)
        pwd = sqlescape(form.password.data)
        
        real_user = session.query(Users).filter(Users.Email == email).first()
        if(real_user is not None and bcrypt.check_password_hash(real_user.Password, pwd)):  
            user = get_user_by_email(email)
            login_user(user) # chiamata a Flask - Login
            return redirect(url_for('home_bp.home'))    
        else:
            if(real_user is None):
                flash('Sembra che tu non sia registrato', 'error')
            else:
                flash('Password errata','error')
            return render_template('login.html',form=form)
    return render_template('login.html',form=form)

@login_bp.route('/subscribe', methods=["GET", "POST"])
def subscribe():
    form = subscribeForm()
    if form.validate_on_submit():
        name = sqlescape(form.name.data)
        email = sqlescape(form.email.data)
        encrypted_pwd = bcrypt.generate_password_hash(sqlescape(form.password.data)).decode('UTF-8')
        profile = form.profile.data
        gender = form.gender.data
        country = form.country.data
        birthday = form.birthday.data
        subs = date.today()

        try:
            if(profile=='Artist'):
                artist = Artists(email, name, birthday, country, gender, encrypted_pwd, profile, subs)
                Artists.create_artist(artist)
            elif(profile=='Premium'):
                premium = Premium(email, name, birthday, country, gender, encrypted_pwd, profile, subs)
                Premium.create_premium(premium)
            else:
                user = Users(email, name, birthday, country, gender, encrypted_pwd, profile, subs)
                Users.create_user(user)
            return redirect(url_for('login_bp.login'))
            
        except exc.SQLAlchemyError as err:
            session.rollback()
            flash("L'indirizzo "+str(email)+" è già associato ad un altro account", 'error')
            return render_template('subscribe.html',form=form)

    return render_template('subscribe.html',form=form)


@login_bp.route('/change_pwd', methods=["GET", "POST"])
def change_pwd():
    form = loginForm()
    if form.validate_on_submit():
        email = sqlescape(form.email.data)
        pwd = bcrypt.generate_password_hash(sqlescape(form.password.data)).decode('UTF-8')

        user = session.query(Users).filter(Users.Email == email).first()
        if(user is not None):
            Users.update_pwd(user, pwd)
            return redirect(url_for('login_bp.login'))
        else:
            flash('Sembra che tu non sia registrato', 'error')
            return redirect(url_for('login_bp.change_pwd', form=form))
    return render_template('change_pwd.html', form=form)

@login_bp.route('/logout')
@login_required # richiede autenticazione
def logout():
    logout_user() # chiamata a Flask - Login
    return redirect(url_for('login_bp.login'))