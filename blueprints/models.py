
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask_login import UserMixin
from flask import Blueprint
from datetime import date


#Vengono creati 4 engine, per connettersi al DB con 4 ruoli diversi e avere gli adeguati permessi

engine = {"free" : create_engine("postgresql://free:free@localhost/prog_db"),
          "premium" : create_engine("postgresql://premium:premium@localhost/prog_db"),
          "artist" : create_engine("postgresql://artist:artist@localhost/prog_db"),
          "admin" : create_engine("postgresql://postgres:Dat4Bas32022!@localhost/prog_db")}

metadata = MetaData()
Base = declarative_base()
Session = sessionmaker(bind=engine["admin"])      
session = Session()


### Definizione tabelle principali ###

#Tabella Users ---> Rappresenta gli utenti dell'applicazione tramite campi e metodi comuni a tutti
#              ---> Campi ---> - Email: l'indirizzo email con cui l'utente si registra all'applicazione (PK) (deve contenere @)
#                              - Name: il nome utente (lunghezza max 20 ch) 
#                              - BirthDate: la data di nascita dell'utente (compresa fra 1/1/1900 e 1/1/2022)
#                              - Country: il paese in cui vive l'utente 
#                              - Gender: il sesso dell' utente (M o F)
#                              - Profile: il tipo di profilo con cui l'utente si registra all'applicazione
#                                         ci sono 3 tipi di profilo : - Free, che è quello base, rappresentato in tutto e 
#                                                                       per tutto dalla tabella Users
#                                                                     - Premium, che si distingue da Free solo per la 
#                                                                       possibilità di fruire di contenuti riservati
#                                                                     - Artist, che oltre alle funzionalità base ha la 
#                                                                       possibilità di creare\eliminare brani e album e 
#                                                                       di fruire di contenuti riservati come i Premium

#                                         nel DB sono stati definiti 3 ruoli con gli stessi nomi e le opportune restrizioni   
#                              - Password: la password con cui l'utente si registra all'applicazione
#                              - SubscribedDate: la data d'iscrizione dell'utente
#             ---> Relazioni con altre tabelle ---> playlists, relazione con Playlists, 
#                                                   rappresenta le playlist create dall'utente
#                                              ---> liked_songs, relazione con Songs, 
#                                                   rappresenta le canzoni a cui l'utente ha messo 'Mi piace'
#                                              ---> liked_albums, relazione con Albums, 
#                                                   rappresenta gli album a cui l'utente ha messo 'Mi piace'
#


class Users(Base, UserMixin):
    __tablename__ = "Users"
  
    Email = Column(String, CheckConstraint(column('Email').like('%@%')), primary_key = True) 
    Name = Column(String(20), nullable = False)
    BirthDate = Column(Date, CheckConstraint(and_(column('BirthDate') > '1/1/1900', column('BirthDate') < '1/1/2008' )), nullable = False)
    Country = Column(String, nullable = False)
    Gender = Column(String, CheckConstraint(or_(column('Gender') == 'M', column('Gender') == 'F')), nullable = False) 
    Profile = Column(String, nullable = False)
    Password = Column(String, nullable = False)
    SubscribedDate = Column(Date, nullable=False)
    
    playlists = relationship('Playlists')
    liked_albums = relationship('Albums', secondary='Users_liked_Albums')
    liked_songs =  relationship('Songs', secondary='Users_liked_Songs')

    __mapper_args__ = {'polymorphic_on': Profile, 'polymorphic_identity': 'Free'}
    
    def __repr__(self): 
        return "<Users(email='%s', name='%s', birth='%s', country='%s', gender='%s', profile='%s')>" % (self.Email, self.Name, self.BirthDate, self.Country, self.Gender, self.Profile)
    
    def __init__(self, email, name, birth, country, gender, password, profile, subs):
        self.Email = email
        self.Name = name
        self.BirthDate = birth
        self.Country = country
        self.Gender = gender
        self.Password = password
        self.Profile = profile
        self.SubscribedDate = subs

    def create_user(self, session): #aggiunge l'utente al DB
        session.add(self)
        session.commit()
        

    def get_id(self): #torna l'ID dell'utente
        return self.Email
    
    def add_playlist(self, playlist, session): #associa una playlist all'utente che l'ha creata
        self.playlists.append(playlist)
        session.commit()
    
    def delete_user(self, session): #cancella l'utente dal DB
        session.query(Users).filter(Users.Email == self.Email).delete()
        session.commit()
    
    def update_user(self, name, session): #aggiorna i campi dell'utente
        session.query(Users).filter(Users.Email == self.Email).update({'Name': name})
        session.commit()
    
    def add_song_to_liked(self, song, session): #associa una canzone all'utente che ha messo 'Mi piace'
        self.liked_songs.append(song)
        session.commit()
    
    def remove_song_from_liked(self, song_id, session): #se l'utente toglie il 'Mi piace' ad una canzone, la loro relazione viene eliminata 
        session.query(Users_liked_Songs).filter(Users_liked_Songs.song_id == song_id, Users_liked_Songs.user_email==self.Email).delete()
        session.commit()
    
    def add_album_to_liked(self, album, session): #associa un album all'utente che ha messo 'Mi piace'
        self.liked_albums.append(album)
        session.commit()
    
    def remove_album_from_liked(self, album_id, session): #se l'utente toglie il 'Mi piace' ad un album, la loro relazione viene eliminata
        session.query(Users_liked_Albums).filter(Users_liked_Albums.album_id == album_id, Users_liked_Albums.user_email==self.Email).delete()
        session.commit()
    
    
    def update_pwd(self, pwd): #aggiorna la password dell'utente
        if(self.Profile == 'Artist'):
            session = Session(bind=engine["artist"])
        if(self.Profile == 'Premium'):
            session = Session(bind=engine["premium"])
        if(self.Profile == 'Free'):
            session = Session(bind=engine["free"])
        
        session.query(Users).filter(Users.Email == self.Email).update({'Password': pwd})
        session.commit()
    
    def update_profile(self, prf, session): #aggiorna il profilo dell'utente (N.B: le playlist vanno preservate)
        if(self.Profile != prf):
            email=self.Email
            nome=self.Name
            pwd=self.Password
            birth=self.BirthDate
            gender=self.Gender
            country=self.Country
            subs=self.SubscribedDate
           
            pl_id = session.query(Playlists.Id).filter(Playlists.User == email).all()
            
            pl_ids=[x[0] for x in pl_id]

            lst_pl=[]
            lst_sng=[]

            for p in pl_ids:
                pl = session.query(Playlists).filter(Playlists.Id==p).first()
                songs = session.query(Songs).filter(Songs.Id.in_(session.query(PlaylistsSongs.song_id).filter(PlaylistsSongs.playlist_id==p))).all()
                for s in songs:
                    lst_sng.append([s.Id, p])
                lst_pl.append([pl.Name, pl.Id, pl.Duration, pl.User])

            
            Users.delete_user(self, session)
            session.close()
            if(prf == 'Artist'):
                session_n = Session(bind=engine["artist"])
                subs_n = date.today()
                artist = Artists(email, nome, birth, country, gender, pwd, prf, subs_n)
                Artists.create_artist(artist, session_n)

                for p in lst_pl:
                    playlist = Playlists(p[0])
                    Playlists.create_playlist(playlist, session_n)
                    for s in lst_sng:
                        if(s[1] == p[1]):
                            song = session_n.query(Songs).filter(Songs.Id == s[0]).first()
                            Playlists.add_song_to_playlist(playlist, song, session_n)

                Users.add_playlist(artist, playlist, session_n)

            elif(prf == 'Premium'):
                session_n = Session(bind=engine["premium"])
                premium = Premium(email, nome, birth, country, gender, pwd, prf, subs)
                Premium.create_premium(premium, session_n)

                for p in lst_pl:
                    playlist = Playlists(p[0])
                    Playlists.create_playlist(playlist, session_n)
                    for s in lst_sng:
                        if(s[1] == p[1]):
                            song = session_n.query(Songs).filter(Songs.Id == s[0]).first()
                            Playlists.add_song_to_playlist(playlist, song, session_n)

                Users.add_playlist(premium, playlist, session_n)

            else:
                session_n = Session(bind=engine["free"])
                user = Users(email, nome, birth, country, gender, pwd, prf, subs)
                Users.create_user(user, session_n)

                for p in lst_pl:
                    playlist = Playlists(p[0])
                    Playlists.create_playlist(playlist, session_n)
                    for s in lst_sng:
                        if(s[1] == p[1]):
                            song = session_n.query(Songs).filter(Songs.Id == s[0]).first()
                            Playlists.add_song_to_playlist(playlist, song, session_n)

                Users.add_playlist(user, playlist, session_n)
        


#Tabella Premium ---> Sottoclasse di Users, contiene solo un campo Email (FK, Users) 
#                     che rappresenta gli indirizzi Email degli utenti Premium

class Premium(Users):
    __mapper_args__ = {'polymorphic_identity': 'Premium'}
    __tablename__ = 'Premium'
    
    Email = Column(None, ForeignKey('Users.Email', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

    def __init__(self, email, name, birth, country, gender, password, profile, subs):
        super().__init__(email, name, birth, country, gender, password, profile, subs)

    def create_premium(self, session): #aggiunge l'utente al DB e popola il rispettivo campo Email in Premium
        print('creo un premium')
        print(self)
        session.add(self)
        session.commit()
        print('commit effettuato')

    
#Tabella Artists ---> Sottoclasse di Users, contiene solo un campo Email (FK, Users) 
#                     che rappresenta gli indirizzi Email degli utenti Artist
#               
#                ---> Relazioni con altre tabelle ---> songs, relazione con Songs, 
#                                                      rappresenta le canzoni create dall'artista
#                                                 ---> albums, relazione con Albums, 
#                                                      rappresenta gli album creati dall'artista
#
class Artists(Users):
    __mapper_args__ = {'polymorphic_identity': 'Artist'}
    __tablename__ = 'Artists'
    
    Email = Column(None, ForeignKey('Users.Email', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

    songs = relationship('Songs')
    albums = relationship('Albums')

    def __init__(self, email, name, birth, country, gender, password, profile, subs):
        super().__init__(email, name, birth, country, gender, password, profile, subs)

    def create_artist(self, session): #aggiunge l'utente al DB e popola il rispettivo campo Email in Artists
        session.add(self)
        session.commit()

    def add_song_if_artist(self, song, session): #associa una canzone all'artista che l'ha creata
        self.songs.append(song)
        session.commit()

    def add_album_if_artist(self, album, session): #associa un album all'artista che l'ha creato 
        self.albums.append(album)
        session.commit()
        
#Tabella Songs ---> rappresenta le canzoni presenti nell'applicazione
#              ---> Campi ---> - Name: il nome della canzone (max 10 ch)
#                              - Duration: la durata della canzone (compresa fra 1 minuto e 30 minuti)
#                              - Genre: il genere della canzone
#                              - Id: l'ID della canzone (PK)
#                              - Is_Restricted: booleano che indica se la canzone è un contenuto Premium(T) o meno(F)
#                              - Artist: l'indirizzo email dell'artista che ha creato la canzone (FK, Artists)
#                              - N_Likes: il numero di 'Mi piace' che ha la canzone
#
#               ---> Relazioni con altre tabelle ---> playlists, relazione con Playlists, 
#                                                     rappresenta le playlist che contengono la canzone
#                                                ---> albums, relazione con Albums,
#                                                     rappresenta gli album che contengono la canzone
#
class Songs(Base):
    __tablename__ = "Songs"
    
    Name = Column(String(10), nullable = False)
    Duration = Column(Time, CheckConstraint(and_(column('Duration') >= '00:01:00', column('Duration') <= '00:30:00' )))
    Genre = Column(String)
    Id = Column(Integer, primary_key = True)
    Is_Restricted = Column(Boolean, nullable = False)
    Artist = Column(String, ForeignKey('Artists.Email', ondelete="CASCADE", onupdate="CASCADE"))
    N_Likes = Column(Integer, CheckConstraint(column('N_Likes') >= 0))
    
  
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

    def create_song(self, session): #aggiunge la canzone al DB
        session.add(self)
        session.commit()
          

    def delete_song(song_id, session): #cancella la canzone dal DB.
        session.query(Songs).filter(Songs.Id == song_id).delete()
        session.commit()

    def update_song(song_id, name, duration, genre, restriction, session): #aggiorna i campi della canzone 
        session.query(Songs).filter(Songs.Id == song_id).update({'Name':name, 'Duration' : duration, 'Genre' : genre, 'Is_Restricted':restriction})
        session.commit()
         

    def update_likes(like, song_id, session): #aggiorna il campo N_LIkes della canzone
        session.query(Songs).filter(Songs.Id == song_id).update({'N_Likes':like})
        session.commit()


#Tabella Albums ---> rappresenta gli album presenti nell'applicazione
#               ---> Campi ---> - Name: il nome dell'album (max 10 ch)
#                               - ReleaseDate: la data di pubblicazione dell'album  
#                               - Duration: la durata dell'album (compresa fra 0 minuti e 1.30 ore)
#                               - Id: l'ID dell'album (PK)
#                               - Record_House: la casa discografica dell'album
#                               - Is_Restricted: booleano che indica se l'album è un contenuto Premium(T) o meno(F)
#                               - Artist: l'indirizzo email dell'artista che ha creato l'album (FK, Artists)
#                               - N_Likes: il numero di 'Mi piace' che ha l'album
#
#               ---> Relazioni con altre tabelle ---> songs, relazione con Songs,
#                                                     rappresenta le canzoni contenute nell'album
#
class Albums(Base):
    __tablename__ = "Albums"

    Name = Column(String(10), nullable = False)
    ReleaseDate = Column(Date)
    Duration = Column(Time, CheckConstraint(and_(column('Duration') >= '00:00:00', column('Duration') <= '01:30:00' )))
    Id = Column(Integer, primary_key = True)
    Record_House = Column(String)
    Is_Restricted = Column(Boolean, nullable = False)
    Artist = Column(String, ForeignKey('Artists.Email', ondelete="CASCADE", onupdate="CASCADE"))
    N_Likes = Column(Integer, CheckConstraint(column('N_Likes') >= 0))
    
    songs = relationship('Songs', secondary = 'AlbumsSongs', back_populates="albums" )

    def __repr__(self):
        return "<Albums(Name='%s', ReleaseDate='%s', Duration='%s', Id='%d', Record_House='%s')>" % (self.Name, self.ReleaseDate, self.Duration, self.Id, self.Record_House)

    def __init__(self, name, record_house, artist, restr, rel):
        self.Name=name
        self.ReleaseDate=rel
        self.Duration='00:00:00'
        self.Record_House=record_house
        self.Artist = artist
        self.Is_Restricted = restr
        self.N_Likes = 0
    
    def create_album(self, session): #aggiunge l'album al DB
        session.add(self)
        session.commit()
    
    def add_song_to_album(self, song, session): #associa una canzone all'album che la contiene
        self.songs.append(song)
        session.commit()
    
    def remove_song(self, song_id, session): #se una canzone viene rimossa dall'album, la loro relazione viene eliminata
        session.query(AlbumsSongs).filter(AlbumsSongs.album_id == self.Id, AlbumsSongs.song_id == song_id).delete()
        session.commit()
    
    def delete_album(album_id, session): #cancella l'album dal DB
        session.query(Albums).filter(Albums.Id == album_id).delete()
        session.commit()
    
    def update_album(album_id, name, releaseDate, record_h, duration, restr, session): #aggiorna i campi dell'album
        session.query(Albums).filter(Albums.Id == album_id).update({'Name':name, 'ReleaseDate':releaseDate, 'Duration' : duration, 'Record_House' : record_h, 'Is_Restricted': restr})
        session.commit()

    def update_likes(like, album_id, session): #aggiorna il campo N_LIkes dell'album
        session.query(Albums).filter(Albums.Id == album_id).update({'N_Likes':like})
        session.commit()   


#Tabella Playlists ---> rappresenta le playlist presenti nell'applicazione
#                  ---> Campi - Name: il nome della playlist (max 10 ch)
#                             - Id: l'ID dell'album (PK)
#                             - Duration: la durata della playlist
#                             - User: l'indirizzo email dell'utente che ha creato la playlist (FK, Users)
#                          
#
#                  ---> Relazioni con altre tabelle ---> songs, relazione con Songs, 
#                                                        rappresenta le canzoni contenute nella playlist
#

class Playlists(Base):
    __tablename__ = "Playlists"

    Name = Column(String(10))
    Id = Column(Integer, primary_key = True)
    Duration = Column(Time)
    User = Column(String, ForeignKey('Users.Email', ondelete="CASCADE", onupdate="CASCADE"))

    songs = relationship('Songs', secondary = 'PlaylistsSongs', back_populates="playlists" )
    
    def __repr__(self):
        return "<Playlists(Name='%s', Id='%d')>" % (self.Name, self.Id)
    
    def __init__(self, name):
        self.Name=name
        self.Duration='00:00:00'
    
    def create_playlist(self, session): #aggiunge la playlist al DB
        session.add(self)
        session.commit()
 
    
    def add_song_to_playlist(self, song, session): #associa una canzone ad una playlist che la contiene
        self.songs.append(song)
        session.commit()
    
    def remove_song(self, song_id, session): #se una canzone viene rimossa da una playlist, la loro relazione viene eliminata
        session.query(PlaylistsSongs).filter(PlaylistsSongs.playlist_id == self.Id, PlaylistsSongs.song_id == song_id).delete()
        session.commit()
    
    def delete_playlist(pl_id, session): #cancella la playlist dal DB
        session.query(Playlists).filter(Playlists.Id == pl_id).delete()
        session.commit()
    
    def update_playlist(pl_id, name, duration, session): #aggiorna i campi della playlist
        session.query(Playlists).filter(Playlists.Id == pl_id).update({'Name':name, 'Duration':duration})
        session.commit()

### Definizione tabelle delle associazioni ###

#Tabella Users_liked_Songs ---> tabella intermedia fra le tabelle Users e Songs per rappresentare l'associazione 
#                               molti a molti fra gli utenti e le canzoni a cui hanno messo 'Mi piace'
#                          ---> Campi ---> song_id: l'ID della canzone piaciuta
#                                     ---> user_email: l'indirizzo email dell'utente che ha messo 'Mi piace'

class Users_liked_Songs(Base):    
    __tablename__ = "Users_liked_Songs"
    
    song_id = Column(Integer, ForeignKey('Songs.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    user_email = Column(String, ForeignKey('Users.Email', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    
    def __repr__(self):
        return "<UsersSongs(song_id='%d', user_email='%s')>" % (self.song_id, self.user_email) 

#Tabella Users_liked_Albums ---> tabella intermedia fra le tabelle Users e Albums per rappresentare l'associazione 
#                                molti a molti fra gli utenti e gli album a cui hanno messo 'Mi piace'
#                           ---> Campi ---> album_id: l'ID dell'album piaciuto
#                                      ---> user_email: l'indirizzo email dell'utente che ha messo 'Mi piace' 

class Users_liked_Albums(Base):    
    __tablename__ = "Users_liked_Albums"
    
    album_id = Column(Integer, ForeignKey('Albums.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    user_email = Column(String, ForeignKey('Users.Email', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    
    def __repr__(self):
        return "<UsersAlbums(album_id='%d', user_email='%s')>" % (self.album_id, self.user_email)

#Tabella AlbumsSongs ---> tabella intermedia fra le tabelle Albums e Songs per rappresentare l'associazione 
#                         molti a molti fra gli album e le canzoni in essi contenute
#                    ---> Campi ---> song_id: l'ID della canzone contenuta nell'album
#                               ---> album_id: l'ID dell'album che contiene la canzone  

class AlbumsSongs(Base):    
    __tablename__ = "AlbumsSongs"
    
    album_id = Column(Integer, ForeignKey('Albums.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    song_id = Column(Integer, ForeignKey('Songs.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    
    def __repr__(self):
        return "<AlbumsSongs(album_id='%d', song_id='%d')>" % (self.album_id, self.song_id)

#Tabella PlaylistsSongs ---> tabella intermedia fra le tabelle Playlists e Songs per rappresentare l'associazione 
#                            molti a molti fra le playlist e le canzoni in esse contenute
#                       ---> Campi ---> song_id: l'ID della canzone contenuta nella playlist
#                                  ---> playlist_id: l'ID della playlist che contiene la canzone  

class PlaylistsSongs(Base):    
    __tablename__ = "PlaylistsSongs"
    
    playlist_id = Column(Integer, ForeignKey('Playlists.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    song_id = Column(Integer, ForeignKey('Songs.Id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    
    def __repr__(self):
        return "<PlaylistsSongs(playlist_id='%d', song_id='%d')>" % (self.playlist_id, self.song_id) 


####################################################################################


################## TRIGGER E FUNZIONI ##################### 


# CREATE TRIGGER "no_same_name_album" BEFORE INSERT OR UPDATE ON "public"."Albums"
# FOR EACH ROW
# EXECUTE PROCEDURE "public"."no_same_name_alb"(); 
#CREATE OR REPLACE FUNCTION "public"."no_same_name_alb"()
#  RETURNS "pg_catalog"."trigger" AS $BODY$BEGIN
#        IF (NEW."Name" IN (SELECT a."Name" 
#                           FROM "public"."Albums" AS a
#                           WHERE a."Artist" = NEW."Artist" and a."Id" != NEW."Id")) THEN
#        RAISE EXCEPTION 'Album con questo nome già presente';
#         END IF;

#         RETURN NEW;
# END$BODY$
#   LANGUAGE plpgsql VOLATILE
#   COST 100;


# CREATE TRIGGER "no_same_name_playlist" BEFORE INSERT OR UPDATE ON "public"."Playlists"
# FOR EACH ROW
# EXECUTE PROCEDURE "public"."no_same_name_pl"();
# CREATE OR REPLACE FUNCTION "public"."no_same_name_pl"()
#   RETURNS "pg_catalog"."trigger" AS $BODY$BEGIN
#         IF (NEW."Name" IN (SELECT p."Name" 
#                            FROM "public"."Playlists" AS p
#                            WHERE p."User" = NEW."User" and p."Id" != NEW."Id")) THEN
#         RAISE EXCEPTION 'Playlist con questo nome già presente';
#         END IF;

#         RETURN NEW;
# END$BODY$
#   LANGUAGE plpgsql VOLATILE
#   COST 100;



# CREATE TRIGGER "no_same_name_song" BEFORE INSERT OR UPDATE ON "public"."Songs"
# FOR EACH ROW
# # EXECUTE PROCEDURE "public"."no_same_name_sng"();
# CREATE OR REPLACE FUNCTION "public"."no_same_name_sng"()
#   RETURNS "pg_catalog"."trigger" AS $BODY$BEGIN
#         IF (NEW."Name" IN (SELECT s."Name" 
#                            FROM "public"."Songs" AS s
#                            WHERE s."Artist" = NEW."Artist" and s."Id" != NEW."Id")) THEN
#         RAISE EXCEPTION 'Brano con questo nome già presente';
#         END IF;

#         RETURN NEW;
# END$BODY$
#   LANGUAGE plpgsql VOLATILE
#   COST 100;

# ALTER FUNCTION "public"."no_same_name_sng"() OWNER TO "postgres";