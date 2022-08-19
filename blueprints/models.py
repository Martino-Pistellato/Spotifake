import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask_login import UserMixin

engine = create_engine("postgresql://postgres:Dat4Bas32022!@localhost/prog_db")
metadata = MetaData()
Base = declarative_base()
Session = sessionmaker(bind=engine)      
session = Session()

### Definizione tabelle principali ###

class Users(Base, UserMixin):
    __tablename__ = "Users"
    
    Email = Column(String, CheckConstraint(column('Email').like('%@%')), primary_key = True) 
    Name = Column(String)
    BirthDate = Column(Date)
    Country = Column(String)
    Gender = Column(String, CheckConstraint(or_(column('Gender') == 'M', column('Gender') == 'F'))) #, CheckConstraint(or_('Gender' == 'M', 'Gender' == 'F'))
    Profile = Column(String, ForeignKey('Profiles.Name'), default = 'Free')
    Password = Column(String, nullable = False)
    
    songs = relationship('Songs', secondary = 'ArtistsSongs', back_populates="artist")
    playlists = relationship('Playlists', secondary = 'PlaylistsUsers', back_populates="users")
    albums = relationship('Albums', secondary = 'ArtistsAlbums', back_populates="artist")
    profile = relationship('Profiles', back_populates="users")
    
    def __repr__(self):
        return "<Users(email='%s', name='%s', birth='%s', country='%s', gender='%s', profile='%s')>" % (self.Email, self.Name, self.BirthDate, self.Country, self.Gender, self.Profile)
    
    def __init__(self, email, name, birth, country, gender, password, profile):
        self.Email = email
        self.Name = name
        self.BirthDate = birth
        self.Country = country
        self.Gender = gender
        self.Password = password
        self.Profile = profile

    def create_user(self):
        session.add(self)
        session.commit()
    
    def get_id(self):
        return self.Email
        
  
class Profiles(Base):
    __tablename__ = "Profiles"
    
    Name = Column(String, primary_key = True)
    
    actions = relationship('Actions', secondary = 'ProfilesActions', back_populates="profiles")
    users = relationship('Users', back_populates="profile") #cascade="all, delete, delete-orphan"
    
    def __repr__(self):
        return "<Profiles(Name='%s')>" % (self.Name)
    
    def __init__(self, name):
        self.Name = name

class Songs(Base):
    __tablename__ = "Songs"
    
    Name = Column(String)
    Duration = Column(Time)
    Genre = Column(String)
    Id = Column(Integer, primary_key = True)
    
    artist = relationship('Users', secondary = 'ArtistsSongs', back_populates="songs")
    playlists = relationship('Playlists', secondary = 'PlaylistsSongs', back_populates="songs")
    albums = relationship('Albums', secondary = 'AlbumsSongs', back_populates="songs")
    
    def __repr__(self):
        return "<Songs(Name='%s', Duration='%s', Genre='%s', Id='%d')>" % (self.Name, self.Duration, self.Genre, self.Id)

class Record_Houses(Base):
    __tablename__ = "Record_Houses"

    Name = Column(String, primary_key = True)

    albums = relationship('Albums', back_populates="record_house")
    
    def __repr__(self):
        return "<Record_Houses(Name='%s')>" % (self.Name)

class Albums(Base):
    __tablename__ = "Albums"

    Name = Column(String)
    ReleaseDate = Column(Date)
    Duration = Column(Time)
    Id = Column(Integer, primary_key = True)
    Record_House = Column(String, ForeignKey(Record_Houses.Name))
    
    artist = relationship('Users', secondary = 'ArtistsAlbums', back_populates="albums")
    songs = relationship('Songs', secondary = 'AlbumsSongs', back_populates="albums")
    record_house = relationship('Record_Houses', back_populates="albums")
    
    def __repr__(self):
        return "<Albums(Name='%s', ReleaseDate='%s', Duration='%s', Id='%d', Record_House='%s')>" % (self.Name, self.ReleaseDate, self.Duration, self.Id, self.Record_House)

class Playlists(Base):
    __tablename__ = "Playlists"

    Name = Column(String)
    Id = Column(Integer, primary_key = True)
    
    users = relationship('Users', secondary = 'PlaylistsUsers', back_populates="playlists")
    songs = relationship('Songs', secondary = 'PlaylistsSongs', back_populates="playlists")
    
    def __repr__(self):
        return "<Playlists(Name='%s', Id='%d')>" % (self.Name, self.Id)

class Actions(Base):
    __tablename__ = "Actions"

    Name = Column(String)
    Id = Column(Integer, primary_key = True)
    
    profiles = relationship('Profiles', secondary = 'ProfilesActions', back_populates="actions")
    
    def __repr__(self):
        return "<Actions(Name='%s', Id='%d')>" % (self.Name, self.Id)

### Definizione tabelle delle associazioni ###

class ArtistsSongs(Base):    
    __tablename__ = "ArtistsSongs"
    
    song_id = Column(Integer, ForeignKey(Songs.Id), primary_key = True)
    artist_email = Column(String, ForeignKey(Users.Email), primary_key = True)
    
    def __repr__(self):
        return "<ArtistsSongs(song_id='%d', artist_email='%s')>" % (self.song_id, self.artist_email)  

class ArtistsAlbums(Base):    
    __tablename__ = "ArtistsAlbums"
    
    album_id = Column(Integer, ForeignKey(Albums.Id), primary_key = True)
    artist_email = Column(String, ForeignKey(Users.Email), primary_key = True)
    
    def __repr__(self):
        return "<ArtistsAlbums(album_id='%d', artist_email='%s')>" % (self.album_id, self.artist_email)  

class AlbumsSongs(Base):    
    __tablename__ = "AlbumsSongs"
    
    album_id = Column(Integer, ForeignKey(Albums.Id), primary_key = True)
    song_id = Column(Integer, ForeignKey(Songs.Id), primary_key = True)
    
    def __repr__(self):
        return "<AlbumsSongs(album_id='%d', song_id='%d')>" % (self.album_id, self.song_id)

class PlaylistsSongs(Base):    
    __tablename__ = "PlaylistsSongs"
    
    playlist_id = Column(Integer, ForeignKey(Playlists.Id), primary_key = True)
    song_id = Column(Integer, ForeignKey(Songs.Id), primary_key = True)
    
    def __repr__(self):
        return "<PlaylistsSongs(playlist_id='%d', song_id='%d')>" % (self.playlist_id, self.song_id) 
    
class PlaylistsUsers(Base):    
    __tablename__ = "PlaylistsUsers"
    
    playlist_id = Column(Integer, ForeignKey(Playlists.Id), primary_key = True)
    user_email = Column(String, ForeignKey(Users.Email), primary_key = True)
    
    def __repr__(self):
        return "<PlaylistsUsers(playlist_id='%d', user_email='%s')>" % (self.playlist_id, self.user_email) 

class ProfilesActions(Base):    
    __tablename__ = "ProfilesActions"
    
    profile_name = Column(String, ForeignKey(Profiles.Name), primary_key = True)
    action_id = Column(Integer, ForeignKey(Actions.Id), primary_key = True)
    
    def __repr__(self):
        return "<ProfilesActions(profile_name='%s', action_id='%d')>" % (self.profile_name, self.action_id)

####################################################################################


Base.metadata.create_all(engine)

Free = Profiles('Free')
Premium = Profiles('Premium')
Artist = Profiles('Artist')

session.add(Free)
session.add(Premium)
session.add(Artist)

session.commit()

