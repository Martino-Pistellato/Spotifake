from flask import Blueprint, render_template, redirect, url_for, flash
from flask import current_app as app
from flask_login import *
from sqlalchemy import exc
from blueprints import *
from ..forms import subscribeForm, loginForm, change_pwdForm
from sqlescapy import sqlescape

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
#Una volta inviati i dati, tramite una query si prende dal DB l'utente avente l'indirizzo email inserito nel form
#Se l'indirizzo è associato ad un utente esistente e la password inserita è uguale alla password (opportunamente decriptata)
#associata all'indirizzo email, l'utente viene loggato e reindirizzato alla home.
#Altrimenti l'utente resterà nella pagina di login
#Vi sono altri due pulsanti: Iscriviti, per iscriversi all'applicazione, e Password dimenticata, per cambiare password

@login_bp.route('/', methods=["GET", "POST"])
def login():
    form = loginForm()
    if form.validate_on_submit():
        email = sqlescape(form.email.data)
        pwd = sqlescape(form.password.data)
        
        real_user = session.query(Users).filter(Users.Email == email).first() #prendi l'utente dal DB
        if(real_user is not None and bcrypt.check_password_hash(real_user.Password, pwd)): #se l'utente esiste e la password è corretta
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


#Route per iscriversi all'applicazione

#A questa pagina può accedere chiunque
#Una volta collezionate tutte le informazioni necessarie per iscrivere l'utente dall'apposito form
#nel blocco try si prova a inserirlo nel DB facendo attenzione a che tipo di profilo è estato scelto
#Se l'azione va a buon fine si torna alla pagina di login
#Se così non dovesse essere, e questo avviene quando 1)i dati sono incompleti (gestito dal form)
#                                                    2)esiste già un account con l'indirizzo email inserito (gestito dal blocco except)
#si restarà sulla pagina dell'iscrizione e verranno mostrati opportuni messaggi d'errore

@login_bp.route('/subscribe', methods=["GET", "POST"])
def subscribe():
    form = subscribeForm()
    if form.validate_on_submit():
        name = sqlescape(form.name.data)
        email = sqlescape(form.email.data)
        encrypted_pwd = bcrypt.generate_password_hash(sqlescape(form.password.data)).decode('UTF-8')#cripta la password
        profile = form.profile.data
        gender = form.gender.data
        country = form.country.data
        birthday = form.birthday.data
        subs = date.today()

        try:
            if(profile=='Artist'):
                session=Session(bind=engine["artist"])
                artist = Artists(email, name, birthday, country, gender, encrypted_pwd, profile, subs)
                Artists.create_artist(artist, session)
            elif(profile=='Premium'):
                session=Session(bind=engine["premium"])
                premium = Premium(email, name, birthday, country, gender, encrypted_pwd, profile, subs)
                Premium.create_premium(premium, session)
            else:
                session=Session(bind=engine["free"])
                user = Users(email, name, birthday, country, gender, encrypted_pwd, profile, subs)
                Users.create_user(user, session)
            return redirect(url_for('login_bp.login'))
            
        except exc.SQLAlchemyError as err:
            session.rollback()
            flash("L'indirizzo "+str(email)+" è già associato ad un altro account", 'error')
            return render_template('subscribe.html',form=form)

    return render_template('subscribe.html',form=form)

#Route per cambiare password

#A questa pagina ha accesso chiunque
#Se sfortunatamente un utente dovesse dimenticare la passwod per il login
#dovrà solo fornire la propria email e una nuova password
#Una volta verificato che l'utente è effettivamente iscritto, si aggiornerà la password
#e l'utente tornerà alla pagina del login da cui potrà finalmente accedere

@login_bp.route('/change_pwd', methods=["GET", "POST"])
def change_pwd():
    form = change_pwdForm()
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

#Route per fare logout

#A questa funzionalità ha accesso chiunque
#Viene fatto logout dell'utente che lo richiede, che viene rimandato al login iniziale

@login_bp.route('/logout')
@login_required # richiede autenticazione
def logout():
    logout_user() # chiamata a Flask - Login
    return redirect(url_for('login_bp.login'))