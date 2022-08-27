from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length

class subscribeForm(FlaskForm):
    name = StringField(
        'Name',
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
        'Profile',
        [DataRequired(message="Scegli con che tipo di account vuoi registrarti")],
        choices=[
            ('Free', 'Free'),
            ('Premium', 'Premium'),
            ('Artist', 'Artist')
        ]
    )
    gender = SelectField(
        'Gender',
        [DataRequired(message="Indica il tuo sesso")],
        choices=[
            ('M', 'M'),
            ('F', 'F')
        ]
    )
    country = StringField(
        'Country',
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