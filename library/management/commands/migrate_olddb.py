'''
migrate users from olddb to library db

I made the design decision to just migrate *everything*. I could also see, equally valid and perhaps more space efficient, a system where we only migrate reviewed albums and then pull in the genres, labels, and artists of those albums.

By migrating everything, however,
* it should be easier for station members to find albums that they remember already being in the DB to review
* if we choose to offline the olddb, then browsing the library db should be easier than spinning that back up from a dump
* it was just a simpler programming task, lol, that's the #1 reason
'''
from django.core.management.base import BaseCommand, CommandError
import mysql.connector
from datetime import datetime
import pytz
from accounts.models import User
from library.models import *

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
            "--migrate-all",
            action="store_true",
            help="migrate everything from olddb",
        )

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
        if options.get("migrate_users", False) or options.get("migrate_all", False):
            migrate_users()

        if options.get("migrate_artists", False) or options.get("migrate_all", False):
            migrate_artists()

        if options.get("migrate_labels", False) or options.get("migrate_all", False):
            migrate_labels()

        if options.get("migrate_genres", False) or options.get("migrate_all", False):
            migrate_genres()

        if options.get("migrate_albums", False) or options.get("migrate_all", False):
            migrate_albums()

        if options.get("migrate_reviews", False) or options.get("migrate_all", False):
            migrate_reviews()

def migrate_users():
    cursor.execute("SELECT UserID, User, FName, LName, DJName, Phone, Email, AuthLevel from Users")
    for old_user in cursor:
        olddb_id, username, fname, lname, djname, phone, email, auth_level = old_user
        if User.objects.filter(olddb_id = olddb_id):
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
                    olddb_id = olddb_id
                )
        new_user.save()
        print(f'created user {username}')

def migrate_artists():
    cursor.execute("SELECT ArtistID, Artist, ShortName, Comment from Artists")
    for old_artist in cursor:
        olddb_id, artist, short_name, comment = old_artist
        if Artist.objects.filter(olddb_id=olddb_id):
            print(f'artist {artist} already exists')
            continue
        new_artist = Artist(
                    artist=artist,
                    short_name = short_name,
                    comment = comment,
                    olddb_id = olddb_id,
                )
        new_artist.save()
        print(f'created artist {artist}')

def migrate_labels():
    cursor.execute("SELECT LabelID, Label, ContactPerson, Email, Address, City, State, Phone from Labels")
    for old_label in cursor:
        olddb_id, label, contact_person, email, address, city, state, phone = old_label
        if Label.objects.filter(olddb_id=olddb_id):
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
                    olddb_id=olddb_id,
                )
        new_label.save()
        print(f'created label {label}')

def migrate_genres():
    cursor.execute("SELECT GenreID, Genre from Genres")
    for old_genre in cursor:
        olddb_id, genre = old_genre
        if Genre.objects.filter(olddb_id=olddb_id):
            print(f'genre {genre} already exists')
            continue
        new_genre = Genre(genre=genre, olddb_id = olddb_id)
        new_genre.save()
        print(f'created genre {genre}')

# an album has a genre, a label, and an artist
def migrate_albums():
    tz = pytz.timezone('America/New_York')
# AlbumID | LabelID | GenreID | ArtistID | FormatID | Album      | Year | HighestChartPosition | DateAdded  | DateRemoved | Status | Comp | ReviewPic | ReleaseNum
    cursor.execute("SELECT AlbumID, LabelID, GenreID, ArtistID, FormatID, Album, Year, DateAdded, DateRemoved, Status from Albums")
    for old_album in cursor:
        olddb_id, label_id, genre_id, artist_id, format_id, album, year, date_added, date_removed, status = old_album
        if Album.objects.filter(olddb_id=olddb_id):
            print(f'album {album} already exists')
            continue

        if date_added and date_added.year < 100:
            date_added = date_added.replace(year = date_added.year + 1900)
        if date_removed and date_removed.year < 100:
            date_removed = date_removed.replace(year = date_removed.year + 1900)

        genres = Genre.objects.filter(olddb_id = genre_id)
        label_obj = Label.objects.filter(olddb_id = label_id).first()
        artist_obj = Artist.objects.filter(olddb_id=artist_id).first()
        new_album = Album(
                album=album,
                artist=artist_obj,
                label=label_obj,
                year=year,
                date_added = date_added,
                date_removed = date_removed,
                status = status,
                olddb_id = olddb_id,
                format = format_id,
            )
        new_album.save()
        if genres:
            new_album.genre.set(genres)
        print(f'created album {album}')

# reviews have a user and album
def migrate_reviews():
    cursor.execute('SELECT ReviewID, UserID, AlbumID, Review, Time from Reviews;')
    for old_review in cursor:
        olddb_id, user_id, album_id, review, date_added = old_review
        if Review.objects.filter(olddb_id=olddb_id):
            print(f'review {olddb_id} already exists')
            continue
        user_obj = User.objects.filter(olddb_id = user_id).first()
        album_obj = Album.objects.filter(olddb_id = album_id).first()

        if date_added and date_added.year < 100:
            date_added = date_added.replace(year = date_added.year + 1900)

        new_review = Review(
                user = user_obj,
                album = album_obj,
                olddb_id = olddb_id,
                review = review,
                date_added = date_added,
                )
        new_review.save()
        print(f'created review {olddb_id}')

