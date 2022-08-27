from email.policy import default
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField, TimeField
from wtforms.validators import DataRequired, Email, Length

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
            DataRequired()
        ]
    )
    password = PasswordField(
        'Password',
        [
            DataRequired(message="Scegli una password"),
            Length(min=8, message=('La password deve essere di almeno 8 caratteri'))
        ]
    )
    
    submit = SubmitField('Submit')
    subscribe = SubmitField('Subscribe')
    
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
            DataRequired(message="Indica la durata della canzone")
        ],
        format='%H:%M:%S',
        render_kw={"step": "1"}
        #default=00:00:00
    )
    genre = StringField(
        'Genere',
        [
            DataRequired(message="Indica il genere della canzone")
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
    
    submit = SubmitField('Submit')
    
    