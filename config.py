"""Flask configuration."""
from os import environ, path

basedir = path.abspath(path.dirname(__file__))

# Database
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Dat4Bas32022!@localhost/prog_db'
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

class Config:
    """Base config."""
    DEBUG = True
    SECRET_KEY = environ.get('SECRRET_KEY')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'