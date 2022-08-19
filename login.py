import secrets
from flask import Flask, redirect, url_for, render_template, make_response, request
from flask_login import *
from sqlalchemy.sql import select
from sqlalchemy import insert
from .blueprints import db
from blueprints.models import *

app=Flask(__name__)
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key

login_manager=LoginManager()
login_manager.init_app(app)


@login_manager.user_loader # attenzione a questo !
def get_user_by_email(email):
    conn = engine.connect()
    res = conn.execute(select([Users]).where(Users.c.email == email))
    user = res.fetchone()
    conn.close()
    return Users(user.email, user.Name, user.BirthDate, user.Country, user.Gender, user.Password)

@app.route('/')
def home():
    # current_user identifica l’utente attuale
    # utente anonimo prima dell ’ autenticazione
    if current_user.is_authenticated :
        return redirect(url_for('private'))
    return render_template("login.html")

@app.route('/private')
@login_required # richiede autenticazione
def private():
    conn = engine.connect()
    all_users = conn.execute(select([Users]))
    resp = make_response(render_template("private.html", users = all_users))
    conn.close()
    return resp


@app.route('/login', methods=['GET', 'POST'])
def login ():
    if request.method == 'POST':
        conn = engine.connect()
        res = conn.execute(select([Users.Password]).where(Users.email == request.form["user"]))
        real_pwd = res.fetchone ()
        conn.close ()
        if(real_pwd is not None and request.form["pass"] == real_pwd["pwd"]):
            user = get_user_by_email(request.form["user"])
            login_user(user) # chiamata a Flask - Login
            return redirect(url_for('private'))    
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


@app.route('/logout')
@login_required # richiede autenticazione
def logout():
    logout_user () # chiamata a Flask - Login
    return redirect(url_for('home'))

@app.route('/subscribe')
def subscribe():
    return render_template("subscribe.html")

@app.route('/create_new_user')
def create_new_user():
    if request.method == 'POST':
        res = Users(request.form["email"], request.form["nome"], request.form["data"], request.form["paese"], request.form["sesso"], request.form["pass"], request.form["profilo"]) #self, email, name, birth, country, gender, password, profile
        Users.create_user(res)
        return render_template("login.html")