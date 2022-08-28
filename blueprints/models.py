import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, validates
from flask_login import UserMixin, current_user
from sqlalchemy import exc
from flask import Blueprint, render_template, request, redirect, url_for

engine = create_engine("postgresql://postgres:Dat4Bas32022!@localhost/prog_db")
metadata = MetaData()
Base = declarative_base()
Session = sessionmaker(bind=engine)      
session = Session()

### Definizione tabelle principali ###

class Users(Base, UserMixin):
    __tablename__ = "Users"
   

    Email = Column(String, CheckConstraint(column('Email').like('%@%')), primary_key = True) 
    Name = Column(String, nullable = False)
    BirthDate = Column(Date, CheckConstraint(and_(column('BirthDate') > '1/1/1900', column('BirthDate') < '1/1/2022' )), nullable = False)
    Country = Column(String, nullable = False)
    Gender = Column(String, CheckConstraint(or_(column('Gender') == 'M', column('Gender') == 'F')), nullable = False) 
    Profile = Column(String, ForeignKey('Profiles.Name', ondelete="CASCADE", onupdate="CASCADE"), nullable = False)
    Password = Column(String, nullable = False)
    
    songs = relationship('Songs')
    playlists = relationship('Playlists')
    albums = relationship('Albums')
   # profile = relationship('Profiles', back_populates="users" )

    #Possibile sistema di like (vogliamo anche che da un oggetto piaciuto si possa risalire agli utenti?)

    liked_albums = relationship('Albums', secondary='UsersAlbums', back_populates="liked_users")
    liked_songs =  relationship('Songs', secondary='UsersSongs', back_populates="liked_users")
    #liked_artists = relationship('Artists', secondary='UsersArtists', back_populates='liked_users')
    
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
        try:
            session.add(self)
            session.commit()
        except exc.SQLAlchemyError as err:
            session.rollback()  
            print(err.orig.diag.message_primary) 
        

    def get_id(self):
        return self.Email
    
    def add_playlist(self, playlist):
        self.playlists.append(playlist)
        session.commit()
    
    def add_song_if_artist(self, song):
        self.songs.append(song)
        session.commit()
    
    def add_album_if_artist(self, album):
        self.albums.append(album)
        session.commit()

    def delete_user(user_email):
        session.query(Users).filter(Users.Email == user_email).delete()
        session.commit()
    
    def update_user(email, name):
        session.query(Users).filter(Users.Email == email).update({'Name': name})
        session.commit()
    
    def add_song_to_liked(self, song):
        self.liked_songs.append(song)
        session.commit()
    
    def add_album_to_liked(self, album):
        self.liked_albums.append(album)
        session.commit()
            
class Profiles(Base):
    __tablename__ = "Profiles"
    
    Name = Column(String, CheckConstraint(or_(column('Name') == 'Free', column('Name') == 'Premium', column('Name') == 'Artist')), primary_key = True)
    
   # actions = relationship('Actions', secondary = 'ProfilesActions', back_populates="profiles" )
    users = relationship('Users') #cascade="all, delete, delete-orphan"
    
    def __repr__(self):
        return "<Profiles(Name='%s')>" % (self.Name)
    
    def __init__(self, name):
        self.Name = name

class Songs(Base):
    __tablename__ = "Songs"
    
    Name = Column(String, nullable = False)
    Duration = Column(Time)
    Genre = Column(String)
    Id = Column(Integer, primary_key = True)
    Is_Restricted = Column(Boolean, nullable = False)
    Artist = Column(String, ForeignKey('Users.Email', ondelete="CASCADE", onupdate="CASCADE"))
    N_Likes = Column(Integer)
    
    liked_users = relationship('Users', secondary= 'UsersSongs', back_populates="liked_songs")
    playlists = relationship('Playlists', secondary = 'PlaylistsSongs', back_populates="songs")
    albums = relationship('Albums', secondary = 'AlbumsSongs', back_populates="songs" )

    def __repr__(self):
        return "<Songs(Name='%s', Duration='%s', Genre='%s', Id='%d')>" % (self.Name, self.Duration, self.Genre, self.Id)

    def __init__(self, name, duration, genre, restriction, artist):
        self.Name = name
        self.Duration = duration
        self.Genre = genre
        self.Is_Restricted = restriction
        self.Artist = artist
        self.N_Likes = 0

    def create_song(self):
        session.add(self)
        session.commit()
    
    def delete_song(song_id):
        session.query(Songs).filter(Songs.Id == song_id).delete()
        session.commit()

    def update_song(song_id, name, duration, genre, restriction):
        session.query(Songs).filter(Songs.Id == song_id).update({'Name':name, 'Duration' : duration, 'Genre' : genre, 'Is_Restricted':restriction})
        session.commit()
    
    def update_likes(like, song_id):
        session.query(Songs).filter(Songs.Id == song_id).update({'N_Likes':like})
        session.commit()


class Record_Houses(Base):
    __tablename__ = "Record_Houses"

    Name = Column(String, primary_key = True)

    albums = relationship('Albums')
    
    def __repr__(self):
        return "<Record_Houses(Name='%s')>" % (self.Name)
    
    def __init__(self, name):
        self.Name = name

class Albums(Base):
    __tablename__ = "Albums"

    Name = Column(String)
    ReleaseDate = Column(Date)
    Duration = Column(Time)
    Id = Column(Integer, primary_key = True)
    Record_House = Column(String, ForeignKey('Record_Houses.Name', ondelete="CASCADE", onupdate="CASCADE"))
    Is_Restricted = Column(Boolean, nullable = False)
    Artist = Column(String, ForeignKey('Users.Email', ondelete="CASCADE", onupdate="CASCADE"))
    N_Likes = Column(Integer)
    
    songs = relationship('Songs', secondary = 'AlbumsSongs', back_populates="albums" )
    liked_users = relationship('Users', secondary= 'UsersAlbums', back_populates="liked_albums")
    
    
    def __repr__(self):
        return "<Albums(Name='%s', ReleaseDate='%s', Duration='%s', Id='%d', Record_House='%s')>" % (self.Name, self.ReleaseDate, self.Duration, self.Id, self.Record_House)

    def __init__(self, name, date, record_house, artist, restr):
        self.Name=name
        self.ReleaseDate=date
        self.Duration='00:00:00'
        self.Record_House=record_house
        self.Artist = artist
        self.Is_Restricted = restr
        self.N_Likes = 0
    
    def create_album(self):
        session.add(self)
        session.commit()
    
    def add_song_to_album(self, song):
        self.songs.append(song)
        session.commit()
    
    def remove_song(self, song_id):
        session.query(AlbumsSongs).filter(AlbumsSongs.album_id == self.Id, AlbumsSongs.song_id == song_id).delete()
        session.commit()
    
    def delete_album(album_id):
        session.query(Albums).filter(Albums.Id == album_id).delete()
        session.commit()
    
    def update_album(album_id, name, releaseDate, record_h, duration, restr):
        session.query(Albums).filter(Albums.Id == album_id).update({'Name':name, 'ReleaseDate':releaseDate, 'Duration' : duration, 'Record_House' : record_h, 'Is_Restricted': restr})
        session.commit()

    def update_likes(like, album_id):
        session.query(Albums).filter(Albums.Id == album_id).update({'N_Likes':like})
        session.commit()   

class Playlists(Base):
    __tablename__ = "Playlists"

    Name = Column(String)
    Id = Column(Integer, primary_key = True)
    User = Column(String, ForeignKey('Users.Email', ondelete="CASCADE", onupdate="CASCADE"))

    #users = relationship('Users', secondary = 'PlaylistsUsers', back_populates="playlists" )
    songs = relationship('Songs', secondary = 'PlaylistsSongs', back_populates="playlists" )
    
    def __repr__(self):
        return "<Playlists(Name='%s', Id='%d')>" % (self.Name, self.Id)
    
    def __init__(self, name):
        self.Name=name
    
    def add_song_to_playlist(self, song):
        self.songs.append(song)
        session.commit()
    
    def remove_song(self, song_id):
        session.query(PlaylistsSongs).filter(PlaylistsSongs.playlist_id == self.Id, PlaylistsSongs.song_id == song_id).delete()
        session.commit()
    
    def delete_playlist(pl_id):
        session.query(Playlists).filter(Playlists.Id == pl_id).delete()
        session.commit()
    
    def update_playlist(pl_id, name):
        session.query(Playlists).filter(Playlists.Id == pl_id).update({'Name':name})
        session.commit()

### Definizione tabelle delle associazioni ###

class UsersSongs(Base):    
    __tablename__ = "UsersSongs"
    
    song_id = Column(Integer, ForeignKey('Songs.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    user_email = Column(String, ForeignKey('Users.Email', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    
    def __repr__(self):
        return "<UsersSongs(song_id='%d', user_email='%s')>" % (self.song_id, self.user_email)  

class UsersAlbums(Base):    
    __tablename__ = "UsersAlbums"
    
    album_id = Column(Integer, ForeignKey('Albums.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    user_email = Column(String, ForeignKey('Users.Email', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    
    def __repr__(self):
        return "<UsersAlbums(album_id='%d', user_email='%s')>" % (self.album_id, self.user_email)  

class AlbumsSongs(Base):    
    __tablename__ = "AlbumsSongs"
    
    album_id = Column(Integer, ForeignKey('Albums.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    song_id = Column(Integer, ForeignKey('Songs.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    
    def __repr__(self):
        return "<AlbumsSongs(album_id='%d', song_id='%d')>" % (self.album_id, self.song_id)

class PlaylistsSongs(Base):    
    __tablename__ = "PlaylistsSongs"
    
    playlist_id = Column(Integer, ForeignKey('Playlists.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    song_id = Column(Integer, ForeignKey('Songs.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    
    def __repr__(self):
        return "<PlaylistsSongs(playlist_id='%d', song_id='%d')>" % (self.playlist_id, self.song_id) 
    
#class PlaylistsUsers(Base):    
#    __tablename__ = "PlaylistsUsers"
    
#    playlist_id = Column(Integer, ForeignKey('Playlists.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
#    user_email = Column(String, ForeignKey('Users.Email', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    
#    def __repr__(self):
#        return "<PlaylistsUsers(playlist_id='%d', user_email='%s')>" % (self.playlist_id, self.user_email) 



####################################################################################

#Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(engine)

#session.add(Profiles('Free'))
#session.add(Profiles('Premium'))
#session.add(Profiles('Artist'))

#session.add(Record_Houses('Bloody'))
#session.add(Record_Houses('Universal'))
#session.add(Record_Houses('Soffro'))

#session.commit()

