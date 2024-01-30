'''
migrate users from olddb to reviews db

I made the design decision to just migrate *everything*. I could also see, equally valid and perhaps more space efficient, a system where we only migrate reviewed albums and then pull in the genres, labels, and artists of those albums.

By migrating everything, however,
* it should be easier for station members to find albums that they remember already being in the DB to review
* if we choose to offline the olddb, then browsing the reviews db should be easier than spinning that back up from a dump
* it was just a simpler programming task, lol, that's the #1 reason
'''
from django.core.management.base import BaseCommand, CommandError
import mysql.connector
from datetime import datetime
import pytz
from accounts.models import User
from reviews.models import *

db = mysql.connector.connect(
  host="olddb.wrct.org",
  port=4306,
  user="www",
  password="fuckyou", # it's a private code repo, but this is a password, lol
  database="wrct",
)

cursor = db.cursor()

class Command(BaseCommand):
    help = "Migrates models from olddb"

    def add_arguments(self, parser):
        parser.add_argument(
            "--migrate-users",
            action="store_true",
            help="migrate users from olddb",
        )

        parser.add_argument(
            "--migrate-artists",
            action="store_true",
            help="migrate artists from olddb",
        )

        parser.add_argument(
            "--migrate-labels",
            action="store_true",
            help="migrate labels from olddb",
        )

        parser.add_argument(
            "--migrate-genres",
            action="store_true",
            help="migrate genres from olddb",
        )

        parser.add_argument(
            "--migrate-albums",
            action="store_true",
            help="migrate albums from olddb",
        )

        parser.add_argument(
            "--migrate-reviews",
            action="store_true",
            help="migrate reviews from olddb",
        )

    def handle(self, *args, **options):
        if options.get("migrate_users", False):
            migrate_users()

        if options.get("migrate_artists", False):
            migrate_artists()

        if options.get("migrate_labels", False):
            migrate_labels()

        if options.get("migrate_genres", False):
            migrate_genres()

        if options.get("migrate_albums", False):
            migrate_albums()

def migrate_users():
    cursor.execute("SELECT User, FName, LName, DJName, Phone, Email, AuthLevel from Users")
    for old_user in cursor:
        username, fname, lname, djname, phone, email, auth_level = old_user
        if User.objects.filter(username = username):
            print(f'user {username} already exists')
            continue
        new_user = User(
                    username = username,
                    first_name = fname,
                    last_name = lname,
                    djname = djname,
                    phone = phone,
                    email = email,
                    auth_level = auth_level if auth_level else "user",
                )
        new_user.save()
        print(f'created user {username}')

def migrate_artists():
    cursor.execute("SELECT Artist, ShortName, Comment from Artists")
    for old_artist in cursor:
        artist, short_name, comment = old_artist
        if Artist.objects.filter(artist=artist, short_name=short_name):
            print(f'artist {artist} already exists')
            continue
        new_artist = Artist(
                    artist=artist,
                    short_name = short_name,
                    comment = comment,
                )
        new_artist.save()
        print(f'created artist {artist}')

def migrate_labels():
    cursor.execute("SELECT Label, ContactPerson, Email, Address, City, State, Phone from Labels")
    for old_label in cursor:
        label, contact_person, email, address, city, state, phone = old_label
        if Label.objects.filter(label=label):
            print(f'label {label} already exists')
            continue
        new_label = Label(
                    label=label,
                    contact_person=contact_person,
                    email=email,
                    address=address,
                    city=city,
                    state=state,
                    phone=phone,
                )
        new_label.save()
        print(f'created label {label}')

def migrate_genres():
    cursor.execute("SELECT Genre from Genres")
    for old_genre in cursor:
        genre = old_genre
        if Genre.objects.filter(genre=genre):
            print(f'genre {genre} already exists')
            continue
        new_genre = Genre(genre=genre)
        new_genre.save()
        print(f'created genre {genre}')

# an album has a genre, a label, and an artist
def migrate_albums():
    tz = pytz.timezone('America/New_York')

    cursor.execute("SELECT Album, Label, Genre, Artist, ShortName, Year, DateAdded, Status from Albums inner join Genres on Albums.GenreID = Genres.GenreID inner join Artists on Albums.ArtistID = Artists.ArtistID inner join Labels on Albums.LabelID = Labels.LabelID")
    for old_album in cursor:
        album, label, genre, artist, short_name, year, date_added, status = old_album
        if Album.objects.filter(album=album, artist__artist=artist):
            print(f'album {album} already exists')
            continue

        if date_added:
            date_added = datetime.combine(date_added, datetime.min.time())

        genres = Genre.objects.filter(genre=genre)
        label_obj = Label.objects.filter(label=label).first()
        artist_obj = Artist.objects.filter(artist=artist, short_name=short_name).first()
        new_album = Album(
                album=album,
                artist=artist_obj,
                label=label_obj,
                year=year,
                date_added = date_added,
                status = status
            )
        new_album.save()
        if genres:
            new_album.genre.set(genres)
        print(f'created album {album}')

# reviews have a user and album
def migrate_reviews():
    cursor.execute
