from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app as app
from flask_login import *
from sqlalchemy import exc
from blueprints import *
from forms import subscribeForm

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
    static_folder='static'
)

@login_bp.route('/')
def login_home():
    return render_template("login.html")

@login_bp.route('/subscribe', methods=["GET", "POST"])
def subscribe():
#    return render_template("subscribe.html")
    form = subscribeForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        encrypted_pwd = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
        profile = form.profile.data
        gender = form.gender.data
        country = form.country.data
        birthday = form.birthday.data
        res = Users(email, name, birthday, country, gender, encrypted_pwd, profile)
        Users.create_user(res)
        return redirect(url_for('login_bp.login_home'))
    return render_template('subscribe.html',form=form)

@login_bp.route('/create_new_user', methods=['GET', 'POST'])
def create_new_user():
    try:
        if request.method == 'POST':
            email = request.form["email"]
            nome = request.form["nome"]
            data = request.form["data"]
            paese = request.form["paese"]
            sesso = request.form["sesso"]
            encrypted_pwd = bcrypt.generate_password_hash(request.form["pass"]).decode('UTF-8')
            profilo = request.form["profilo"]
            res = Users(email, nome, data, paese, sesso, encrypted_pwd, profilo) 
            Users.create_user(res)
            return redirect(url_for('login_bp.login_home'))
    except exc.SQLAlchemyError as err:
        session.rollback()   
        return redirect(url_for('login_bp.subscribe')) 


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        real_user = session.query(Users).filter(Users.Email == request.form["user"]).first()
        if(real_user is not None and bcrypt.check_password_hash(real_user.Password, request.form["pass"]) ):  
            user = get_user_by_email(request.form["user"])
            login_user(user) # chiamata a Flask - Login
            return redirect(url_for('home_bp.home'))    
        else:
            return redirect(url_for('login_bp.login_home'))
    else:
        return redirect(url_for('login_bp.login_home'))

@login_bp.route('/logout')
@login_required # richiede autenticazione
def logout():
    logout_user() # chiamata a Flask - Login
    return redirect(url_for('login_bp.login_home'))