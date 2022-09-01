from email.policy import default
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField, TimeField
from wtforms.validators import DataRequired, Email, Length, ValidationError
import datetime
from datetime import date

class subscribeForm(FlaskForm):
    name = StringField(
        'Nome',
        [
            DataRequired(message="Indica un nome utente")
        ]
    )
    email = StringField(
        'Email',
        [
            Email(message='Indirizzo email non valido'),
            DataRequired(message="Fornisci un indirizzo email")
        ]
    )
    password = PasswordField(
        'Password',
        [
            DataRequired(message="Scegli una password"),
            Length(min=8, message=('La password deve essere di almeno 8 caratteri'))
        ]
    )
    profile = SelectField(
        'Profilo',
        [DataRequired(message="Scegli con che tipo di account vuoi registrarti")],
        choices=[
            ('Free', 'Free'),
            ('Premium', 'Premium'),
            ('Artist', 'Artist')
        ]
    )
    gender = SelectField(
        'Sesso',
        [DataRequired(message="Indica il tuo sesso")],
        choices=[
            ('M', 'M'),
            ('F', 'F')
        ]
    )
    country = StringField(
        'Paese',
        [
            DataRequired(message="Seleziona una nazione")
        ]
    )
    birthday = DateField(
        'La tua data di nascita',
        [DataRequired(message="Indica la tua data di nascita")]
    )
    
    submit = SubmitField('Submit')
    
class loginForm(FlaskForm):
    email = StringField(
        'Email',
        [
            Email(message='Indirizzo email non valido'),
            DataRequired(message="Inserisci l'indirizzo email")
        ]
    )
    password = PasswordField(
        'Password',
        [
            DataRequired(message="Scegli una password"),
            Length(min=8, message=('La password deve essere di almeno 8 caratteri'))
        ]
    )
    
    submit = SubmitField('Login')
    subscribe = SubmitField('Subscribe')


def time_check_song(form, field):
    t = field.data
    if (t.hour > 0 or t.minute > 30 or (t.minute == 30 and t.second > 0)):
        raise ValidationError('Un brano deve avere una durata massima di 30 minuti')
    elif(t.hour == 0 and t.minute == 0):
        raise ValidationError('Un brano deve avere una durata minima di 1 minuto')

class upload_SongForm(FlaskForm):
    name = StringField(
        'Nome',
        [
            DataRequired(message="Indica il nome della canzone")
        ]
    )
    time = TimeField(
        'Durata',
        [
            DataRequired(message="Indica la durata della canzone"), time_check_song
        ],
        format='%H:%M:%S',
        render_kw={"step": "1"},
        default=datetime.time(0,0,0)
    )
    genre = SelectField(
        'Genere',
        [
            DataRequired(message="Indica il genere della canzone")
        ],
        choices=[
            ('Rap', 'Rap'),
            ('Pop', 'Pop'),
            ('Country', 'Country'),
            ('Techno', 'Techno'),
            ('Rock', 'Rock'),
            ('Metal', 'Metal'),
            ('Classic', 'Classic'),
            ('Neomelodico Napoletano', 'Neomelodico Napoletano')
        ]
    )
    type = SelectField(
        'Visibilità',
        [DataRequired(message="Indica quali account possono vedere la canzone")],
        choices=[
            ('Free', 'Free'),
            ('Premium', 'Premium')
        ]
    )
    
    submit = SubmitField('Salva')
    
class upload_AlbumForm(FlaskForm):
    name = StringField(
        'Nome',
        [
            DataRequired(message="Indica il nome dell'album")
        ]
    )
    releaseDate = DateField(
        'Data di pubblicazione',
        [
            DataRequired(message="Indica la data di pubblicazione")
        ],
        default=date.today()
    )
    recordHouse = SelectField(
        'Casa discografica',
        [
            DataRequired(message="Indica la casa discografica")
        ],
        choices=[
            ('Universal', 'Universal'),
            ('Bloody', 'Bloody'),
            ('Warner Brothers', 'Warner Brothers'),
            ('Bicho Malo', 'Bicho Malo')
        ]
    )
    type = SelectField(
        'Visibilità',
        [DataRequired(message="Indica quali account possono vedere la canzone")],
        choices=[
            ('Free', 'Free'),
            ('Premium', 'Premium')
        ]
    )
    
    submit = SubmitField('Salva')
    
class upload_PlaylistForm(FlaskForm):
    name = StringField(
        'Nome',
        [
            DataRequired(message="Indica il nome della playlist")
        ]
    )
    
    submit = SubmitField('Salva')