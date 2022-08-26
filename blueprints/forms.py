from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length

class subscribeForm(FlaskForm):
    name = StringField(
        'Name',
        [
            DataRequired(message="Please choose a name.")
        ]
    )
    email = StringField(
        'Email',
        [
            Email(message='Not a valid email address.'),
            DataRequired()
        ]
    )
    password = PasswordField(
        'Password',
        [
            DataRequired(message="Please enter a password."),
            Length(min=8, message=('Too short'))
        ]
    )
    profile = SelectField(
        'Profile',
        [DataRequired()],
        choices=[
            ('Free', 'Free'),
            ('Premium', 'Premium'),
            ('Artist', 'Artist')
        ]
    )
    gender = SelectField(
        'Gender',
        [DataRequired()],
        choices=[
            ('M', 'M'),
            ('F', 'F')
        ]
    )
    country = StringField(
        'Country',
        [
            DataRequired(message="Please choose a country.")
        ]
    )
    birthday = DateField(
        'Your Birthday',
        [DataRequired()]
    )
    
    submit = SubmitField('Submit')
    
class loginForm(FlaskForm):
    email = StringField(
        'Email',
        [
            Email(message='Not a valid email address.'),
            DataRequired()
        ]
    )
    password = PasswordField(
        'Password',
        [
            DataRequired(message="Please enter a password."),
            Length(min=8, message=('Too short'))
        ]
    )
    
    submit = SubmitField('Submit')