import secrets
from flask import Flask, redirect, url_for, render_template, make_response, request
from flask_login import *
from sqlalchemy.sql import select
from sqlalchemy import insert
from . import db
from blueprints.models import *

app=Flask(__name__)
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key

login_manager=LoginManager()
login_manager.init_app(app)


@app.route('/')
def home():
    # current_user identifica l’utente attuale
    # utente anonimo prima dell ’ autenticazione
    if current_user.is_authenticated :
        return redirect(url_for('private'))
    return render_template("login.html")




