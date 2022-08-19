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
        
        # Register Blueprints
        #app.register_blueprint(home.home_bp)
        #app.register_blueprint(profile.profile_bp)
        app.register_blueprint(log.login_bp)
        
        # Create Database
        db.create_all()
        
        return app