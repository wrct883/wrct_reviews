from django.db import models
from django.utils import timezone
from datetime import date
from accounts.models import User

from django.urls import reverse

class Artist(models.Model):
    artist = models.CharField(max_length=255, default='')
    short_name = models.CharField(max_length=6, null=True, blank=True)
    comment = models.TextField(null = True, blank = True)
    olddb_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.artist

    def get_absolute_url(self):
        return reverse('library:detail', kwargs = {'table': 'artist', 'pk': self.pk})

    @property
    def table(self):
        return "artist"

    @property
    def json(self):
        return {"name": str(self),
                "id": self.id}

class Label(models.Model):
    label = models.CharField(max_length=255, default='')
    contact_person = models.CharField(max_length=80, null=True, blank=True)
    email = models.CharField(max_length=80, null=True, blank=True)
    address = models.CharField(max_length=80, null=True, blank=True)
    city = models.CharField(max_length=80, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    phone = models.CharField(max_length=80, null=True, blank=True)
    comment = models.TextField(null = True, blank = True)
    olddb_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse('library:detail', kwargs = {'table': 'label', 'pk': self.pk})

    @property
    def table(self):
        return "label"

    @property
    def json(self):
        return {"name": str(self),
                "id": self.id}

class Genre(models.Model):
    genre = models.CharField(max_length=80, default='')
    olddb_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.genre

    def get_absolute_url(self):
        return reverse('library:detail', kwargs = {'table': 'genre', 'pk': self.pk})

    @property
    def table(self):
        return "genre"

    @property
    def json(self):
        return {"name": str(self),
                "id": self.id}

class Album(models.Model):
    album = models.CharField(max_length=255, default='')
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True)
    label = models.ForeignKey(Label, on_delete=models.SET_NULL, null=True, blank=True)
    genre = models.ManyToManyField(Genre, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    date_added = models.DateField(default=date.today, null=True)
    date_removed = models.DateField(null=True, blank=True)

    STATUS_CHOICES = [
        ("Bin", "Bin"),
        ("N&WC", "N&WC (??)"),
        ("NIB", "Not in bin"),
        ("TBR", "To be reviewed"),
        ("OOB", "Out of bin"),
    ]

    status = models.CharField(max_length=4, null=True, blank=True, choices=STATUS_CHOICES)

    FORMAT_CHOICES = [
        (12, "LP"),
        (11, '12" vinyl'),
        (10, '10" vinyl'),
        (9, 'EP single'),
        (8, '7" vinyl'),
        (7, "CD"),
        (14, "Kassette"),
        (15, '7"'),
        (16, 'EP'),
        (17, 'Digital'),
    ]
    # these values are vestigial structures from olddb, lol

    format = models.IntegerField(choices=FORMAT_CHOICES, null=True, blank=True)

    olddb_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.album

    class Meta:
        ordering =  ('-date_added', 'album',)

    def get_absolute_url(self):
        return reverse('library:detail', kwargs = {'table': 'album', 'pk': self.pk})

    @property
    def table(self):
        return "album"

    @property
    def json(self):
        return {"name": str(self),
                "id": self.id,
                "artist": str(self.artist if self.artist else ""),
                "label": str(self.label if self.label else "")}


class Review(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    date_added = models.DateTimeField(default=timezone.now)
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True)
    review = models.TextField(default='')
    olddb_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"of {self.album} by {self.user}"

    class Meta:
        ordering =  ('-date_added',)

    def get_absolute_url(self):
        return reverse('library:detail', kwargs = {'table': 'review', 'pk': self.pk})

    @property
    def table(self):
        return "review"

    @property
    def json(self):
        return {"name": str(self),
                "id": self.id}

