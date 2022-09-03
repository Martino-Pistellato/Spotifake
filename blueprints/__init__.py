"""Initialize Flask app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import *
from blueprints.models import *

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager=LoginManager()


def create_app(): #Crea applicazione Flask
    
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    with app.app_context(): # Importa e configura le componenti necessarie per il corretto funzionamento dell'applicazione 
        from .home import routes
        from .profile import routes
        from .log import routes
        from .album import routes
        from .playlist import routes
        from .find import routes
        from .lib import routes
        from .stats import routes
        from .song import routes
        from .artist import routes

        app.register_blueprint(home.routes.home_bp)
        app.register_blueprint(profile.routes.profile_bp)
        app.register_blueprint(log.routes.login_bp)
        app.register_blueprint(album.routes.album_bp)
        app.register_blueprint(playlist.routes.playlist_bp)
        app.register_blueprint(find.routes.find_bp)
        app.register_blueprint(lib.routes.library_bp)
        app.register_blueprint(stats.routes.stats_bp)
        app.register_blueprint(song.routes.song_bp)
        app.register_blueprint(artist.routes.artist_bp)

        db.create_all()
        
        return app

