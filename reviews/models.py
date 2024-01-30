from django.db import models
from django.utils import timezone
from accounts.models import User

class Artist(models.Model):
    artist = models.CharField(max_length=255, default='')
    short_name = models.CharField(max_length=6, null=True, blank=True)
    comment = models.TextField(null = True, blank = True)

    def __str__(self):
        return self.artist

    class Meta:
        unique_together = ('artist', 'short_name',)



class Label(models.Model):
    label = models.CharField(max_length=255, default='')
    contact_person = models.CharField(max_length=80, null=True, blank=True)
    email = models.CharField(max_length=80, null=True, blank=True)
    address = models.CharField(max_length=80, null=True, blank=True)
    city = models.CharField(max_length=80, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    phone = models.CharField(max_length=80, null=True, blank=True)
    comment = models.TextField(null = True, blank = True)

    def __str__(self):
        return self.label

class Genre(models.Model):
    genre = models.CharField(max_length=80, default='')

    def __str__(self):
        return self.genre

class Album(models.Model):
    album = models.CharField(max_length=255, default='')
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True)
    label = models.ForeignKey(Label, on_delete=models.SET_NULL, null=True, blank=True)
    genre = models.ManyToManyField(Genre, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now, null=True)

    STATUS_CHOICES = [
        ("Bin", "Bin"),
        ("N&WC", "N&WC (??)"),
        ("NIB", "Not in bin"),
        ("TBR", "To be reviewed"),
        ("OOB", "Out of bin"),
    ]

    status = models.CharField(max_length=4, null=True, blank=True, choices=STATUS_CHOICES)

    def __str__(self):
        return self.album

class Review(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    date_added = models.DateTimeField(default=timezone.now)
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True)
    review = models.TextField(default='')

    def __str__(self):
        return f"review by {self.user}"

