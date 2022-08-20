from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app as app
from blueprints.models import *
from flask_login import *

login_manager=LoginManager()
login_manager.init_app(app)

# Blueprint Configuration
login_bp = Blueprint(
    'login_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@login_bp.route('/')
def login_home():
    return render_template("login.html")

@login_bp.route('/subscribe')
def subscribe():
    return render_template("subscribe.html")

@login_bp.route('/create_new_user', methods=['GET', 'POST'])
def create_new_user():
    if request.method == 'POST':
        conn = engine.connect()
        us = conn.execute(select([Users]).where(Users.Email == request.form["email"]))
        existing_user = us.fetchone()
        conn.close()
        if(existing_user is None):
            email = request.form["email"]
            nome = request.form["nome"]
            data = request.form["data"]
            paese = request.form["paese"]
            sesso = request.form["sesso"]
            pwd = request.form["pass"]
            profilo = request.form["profilo"]
            if(email is not None and nome is not None and data is not None and paese is not None and sesso is not None and pwd is not None):
                res = Users(email, nome, data, paese, sesso, pwd, profilo) 
                Users.create_user(res)
                return redirect(url_for('login_bp.login_home'))
        return redirect(url_for('login_bp.subscribe'))


@login_manager.user_loader # attenzione a questo !
def get_user_by_email(email):
    conn = engine.connect()
    res = conn.execute(select([Users]).where(Users.Email == email))
    user = res.fetchone()
    conn.close()
    return Users(user.Email, user.Name, user.BirthDate, user.Country, user.Gender, user.Password, user.Profile)

@login_bp.route('/login', methods=['GET', 'POST'])
def login ():
    if request.method == 'POST':
        conn = engine.connect()
        res = conn.execute(select([Users]).where(Users.Email == request.form["user"]))
        real_us = res.fetchone ()
        conn.close ()
        if(real_us is not None and request.form["pass"] == real_us.Password): 
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
    logout_user () # chiamata a Flask - Login
    return redirect(url_for('login_bp.login_home'))