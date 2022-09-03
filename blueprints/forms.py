from email.policy import default
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField, TimeField
from wtforms.validators import DataRequired, Email, Length, ValidationError
import datetime
from datetime import date

### Funzioni per gestire errori nei form

def time_check_song(form, field):
    t = field.data
    if (t.hour > 0 or t.minute > 30 or (t.minute == 30 and t.second > 0)):
        raise ValidationError('Un brano deve avere una durata massima di 30 minuti')
    elif(t.hour == 0 and t.minute == 0):
        raise ValidationError('Un brano deve avere una durata minima di 1 minuto')

def len_name_song(form, field):
    if(len(field.data) > 10):
        raise ValidationError('Il titolo di un brano deve avere una lunghezza massima di 10 caratteri')

def len_name_alb(form, field):
    if(len(field.data) > 10):
        raise ValidationError('Il titolo di un album deve avere una lunghezza massima di 10 caratteri')

def len_name_pl(form, field):
    if(len(field.data) > 10):
        raise ValidationError('Il titolo di una playlist deve avere una lunghezza massima di 10 caratteri')

def len_name_user(form, field):
    if(len(field.data) > 20):
        raise ValidationError('Il tuo nome utente deve avere una lunghezza massima di 20 caratteri')

#Forms

class subscribeForm(FlaskForm): #Form per iscriversi all'applicazione
    name = StringField(
        'Nome',
        [
            DataRequired(message="Indica un nome utente"), len_name_user
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
    country = SelectField(
        'Paese',
        [
            DataRequired(message="Seleziona una nazione")
        ],
         choices=[
            ('Afghanistan', 'Afghanistan'),
            ('Albania', 'Albania'),
            ('Algeria','Algeria'),
            ('Andorra','Andorra'),
            ('Angola','Angola'),
            ('Antigua e Barbuda','Antigua e Barbuda'),
            ('Arabia Saudita','Arabia Saudita'),
            ('Argentina','Argentina'),
            ('Armenia','Armenia'),
            ('Australia','Australia'),
            ('Austria','Austria'),
            ('Azerbaijan','Azerbaijan'),
            ('Bahamas','Bahamas'),
            ('Bahrain','Bahrain'),
            ('Bangladesh','Bangladesh'),
            ('Barbados','Barbados'),
            ('Belgio','Belgio'),
            ('Belize','Belize'),
            ('Benin','Benin'),
            ('Bhutan','Bhutan'),
            ('Bielorussia','Bielorussia'),
            ('Birmania','Birmania'),
            ('Bolivia','Bolivia'),
            ('Bosnia ed Erzegovina','Bosnia ed Erzegovina'),
            ('Botswana','Botswana'),
            ('Brasile','Brasile'),
            ('Brunei','Brunei'),
            ('Bulgaria','Bulgaria'),
            ('Burkina Faso','Burkina Faso'),
            ('Burundi','Burundi'),
            ('Cambogia','Cambogia'),
            ('Camerun','Camerun'),
            ('Canada','Canada'),
            ('Capo Verde','Capo Verde'),
            ('Ciad','Ciad'),
            ('Cile','Cile'),
            ('Cina','Cina'),
            ('Cipro','Cipro'),
            ('Colombia','Colombia'),
            ('Comore','Comore'),
            ('Congo','Congo'),
            ('Corea del Nord','Corea del Nord'),
            ('Corea del Sud','Corea del Sud'),
            ("Costa d'Avorio","Costa d'Avorio"),
            ('Costa Rica','Costa Rica'),
            ('Croazia','Croazia'),
            ('Cuba','Cuba'),
            ('Danimarca','Danimarca'),
            ('Dominica','Dominica'),
            ('Ecuador','Ecuador'),
            ('Egitto','Egitto'),
            ('El Salvador','El Salvador'),
            ('Emirati Arabi Uniti','Emirati Arabi Uniti'),
            ('Eritrea','Eritrea'),
            ('Estonia','Estonia'),
            ('eSwatini','eSwatini'),
            ('Etiopia','Etiopia'),
            ('Figi','Figi'),
            ('Filippine','Filippine'),
            ('Finlandia','Finlandia'),
            ('Francia','Francia'),
            ('Gabon','Gabon'),
            ('Gambia','Gambia'),
            ('Georgia','Georgia'),
            ('Germania','Germania'),
            ('Ghana','Ghana'),
            ('Giamaica','Giamaica'),
            ('Giappone','Giappone'),
            ('Gibuti','Gibuti'),
            ('Giordania','Giordania'),
            ('Grecia','Grecia'),
            ('Grenada','Grenada'),
            ('Guatemala','Guatemala'),
            ('Guinea','Guinea'),
            ('Guinea Equatoriale','Guinea Equatoriale'),
            ('Guinea-Bissau','Guinea-Bissau'),
            ('Guyana','Guyana'),
            ('Haiti','Haiti'),
            ('Honduras','Honduras'),
            ('India','India'),
            ('Indonesia','Indonesia'),
            ('Iran','Iran'),
            ('Iraq','Iraq'),
            ('Irlanda','Irlanda'),
            ('Islanda','Islanda'),
            ('Isole Marshall','Isole Marshall'),
            ('Isole Salomone','Isole Salomone'),
            ('Israele','Israele'),
            ('Italia','Italia'),
            ('Kazakistan','Kazakistan'),
            ('Kenya','Kenya'),
            ('Kirghizistan','Kirghizistan'),
            ('Kiribati','Kiribati'),
            ('Kosovo','Kosovo'),
            ('Kuwait','Kuwait'),
            ('Laos','Laos'),
            ('Lesotho','Lesotho'),
            ('Lettonia','Lettonia'),
            ('Libano','Libano'),
            ('Liberia','Liberia'),
            ('Libia','Libia'),
            ('Liechtenstein','Liechtenstein'),
            ('Lituania','Lituania'),
            ('Lussemburgo','Lussemburgo'),
            ('Macedonia del Nord','Macedonia del Nord'),
            ('Madagascar','Madagascar'),
            ('Malawi','Malawi'),
            ('Maldive','Maldive'),
            ('Malesia','Malesia'),
            ('Mali','Mali'),
            ('Malta','Malta'),
            ('Marocco','Marocco'),
            ('Mauritania','Mauritania'),
            ('Mauritius','Mauritius'),
            ('Messico','Messico'),
            ('Micronesia','Micronesia'),
            ('Moldavia','Moldavia'),
            ('Monaco','Monaco'),
            ('Mongolia','Mongolia'),
            ('Montenegro','Montenegro'),
            ('Mozambico','Mozambico'),
            ('Namibia','Namibia'),
            ('Nauru','Nauru'),
            ('Nepal','Nepal'),
            ('Nicaragua','Nicaragua'),
            ('Niger','Niger'),
            ('Nigeria','Nigeria'),
            ('Norvegia','Norvegia'),
            ('Nuova Zelanda','Nuova Zelanda'),
            ('Oman','Oman'),
            ('Paesi Bassi','Paesi Bassi'),
            ('Pakistan','Pakistan'),
            ('Palau','Palau'),
            ('Palestina','Palestina'),
            ('Panamá','Panamá'),
            ('Papua Nuova Guinea','Papua Nuova Guinea'),
            ('Paraguay','Paraguay'),
            ('Perù','Perù'),
            ('Polonia','Polonia'),
            ('Portogallo','Portogallo'),
            ('Qatar','Qatar'),
            ('Regno Unito','Regno Unito'),
            ('Repubblica Ceca','Repubblica Ceca'),
            ('Repubblica Centrafricana','Repubblica Centrafricana'),
            ('Repubblica Democratica del Congo','Repubblica Democratica del Congo'),
            ('Repubblica Dominicana','Repubblica Dominicana'),
            ('Romania','Romania'),
            ('Ruanda','Ruanda'),
            ('Russia','Russia'),
            ('Saint Kitts e Nevis','Saint Kitts e Nevis'),
            ('Saint Vincent e Grenadine','Saint Vincent e Grenadine'),
            ('Samoa','Samoa'),
            ('San Marino','San Marino'),
            ('Santa Lucia','Santa Lucia'),
            ('São Tomé e Príncipe','São Tomé e Príncipe'),
            ('Senegal','Senegal'),
            ('Serbia','Serbia'),
            ('Seychelles','Seychelles'),
            ('Sierra Leone','Sierra Leone'),
            ('Singapore','Singapore'),
            ('Siria','Siria'),
            ('Slovacchia','Slovacchia'),
            ('Slovenia','Slovenia'),
            ('Somalia','Somalia'),
            ('Spagna','Spagna'),
            ('Sri Lanka','Sri Lanka'),
            ('Stati Uniti','Stati Uniti'),
            ('Sudafrica','Sudafrica'),
            ('Sudan','Sudan'),
            ('Sudan del Sud','Sudan del Sud'),
            ('Suriname','Suriname'),
            ('Svezia','Svezia'),
            ('Svizzera','Svizzera'),
            ('Tagikistan','Tagikistan'),
            ('Taiwan','Taiwan'),
            ('Tanzania','Tanzania'),
            ('Thailandia','Thailandia'),
            ('Timor Est','Timor Est'),
            ('Togo','Togo'),
            ('Tonga','Tonga'),
            ('Trinidad e Tobago','Trinidad e Tobago'),
            ('Tunisia','Tunisia'),
            ('Turchia','Turchia'),
            ('Turkmenistan','Turkmenistan'),
            ('Tuvalu','Tuvalu'),
            ('Ucraina','Ucraina'),
            ('Uganda','Uganda'),
            ('Ungheria','Ungheria'),
            ('Uruguay','Uruguay'),
            ('Uzbekistan','Uzbekistan'),
            ('Vanuatu','Vanuatu'),
            ('Vaticano','Vaticano'),
            ('Venezuela','Venezuela'),
            ('Vietnam','Vietnam'),
            ('Yemen','Yemen'),
            ('Zambia','Zambia'),
            ('Zimbabwe','Zimbabwe'),
        ]
    )
    birthday = DateField(
        'La tua data di nascita',
        [DataRequired(message="Indica la tua data di nascita")]
    )
    
    submit = SubmitField('Invia')


class update_profileForm(FlaskForm): #Form per aggiornare il profilo utente
    name = StringField(
        'Nome',
        [
            DataRequired(message="Indica un nome utente"), len_name_user
        ]
    )
    profile = SelectField(
        'Profilo',
        [DataRequired(message="Cambia tipo di account")],
        choices=[
            ('Free', 'Free'),
            ('Premium', 'Premium'),
            ('Artist', 'Artist')
        ]
    )
    submit = SubmitField('Invia')

    
class loginForm(FlaskForm): #Form per accedere all'applicazione
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
    
    submit = SubmitField('Invia')
    subscribe = SubmitField('Iscriviti')
    pwd_dimenticata = SubmitField('Password dimenticata')


class change_pwdForm(FlaskForm): #Form per cambiare password
    email = StringField(
        'Email',
        [
            Email(message='Indirizzo email non valido'),
            DataRequired(message="Inserisci l'indirizzo email")
        ]
    )
    password = PasswordField(
        'Nuova password',
        [
            DataRequired(message="Scegli una nuova password"),
            Length(min=8, message=('La password deve essere di almeno 8 caratteri'))
        ]
    )
    
    submit = SubmitField('Salva')


class upload_SongForm(FlaskForm): #Form per caricare una canzone
    name = StringField(
        'Nome',
        [
            DataRequired(message="Indica il nome della canzone"), len_name_song
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
    
class upload_AlbumForm(FlaskForm): #Form per caricare un album
    name = StringField(
        'Nome',
        [
            DataRequired(message="Indica il nome dell'album"), len_name_alb
        ]
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
            ('Bicho Malo', 'Bicho Malo'),
            ('Indipendente', 'Indipendente')
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
    
class upload_PlaylistForm(FlaskForm): #Form per caricare una playlist
    name = StringField(
        'Nome',
        [
            DataRequired(message="Indica il nome della playlist"), len_name_pl
        ]
    )
    
    submit = SubmitField('Salva')