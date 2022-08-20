"""Initialize Flask app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    """Create Flask application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    db.init_app(app)
    
    with app.app_context():
        # Import parts of our application
        from .home import routes
        from .profile import routes
        from .log import routes
        from .album import routes
        from .playlist import routes
        from .library import routes
        from .find import routes
        
        # Register Blueprints
        app.register_blueprint(home.routes.home_bp)
        app.register_blueprint(profile.routes.profile_bp)
        app.register_blueprint(log.routes.login_bp)
        app.register_blueprint(album.routes.album_bp)
        app.register_blueprint(playlist.routes.playlist_bp)
        app.register_blueprint(library.routes.library_bp)
        app.register_blueprint(find.routes.find_bp)
        
        # Create Database
        db.create_all()
        
        return app