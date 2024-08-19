from django.db import models
from django.utils import timezone
from datetime import date, datetime
from django.contrib.auth.models import AbstractUser
from django.core.serializers.json import DjangoJSONEncoder

from django.urls import reverse

from django.apps import apps
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
import copy


DETAIL_FIELDS = {
    'Album': ('album', 'artist', 'label', 'genre', 'subgenre', 'year', 'date_added', 'date_removed', 'status', 'format'),
    'Artist': ('artist', 'comment'),
    'Genre': ('genre',),
    'Subgenre': ('genre', 'subgenre'),
    'Label': ('label', 'contact_person', 'email', 'address', 'city', 'state', 'phone', 'comment'),
    'Review': ('user', 'date_added', 'album', 'review'),
    'User': ('username', 'first_name', 'last_name', 'djname', 'phone', 'email', 'date_trained', 'auth_level'),
}
SEARCH_FIELDS = {
    'Album': ['album', 'artist'],
    'Artist': ['artist',],
    'Genre': ['genre'],
    'Subgenre': ['genre', 'subgenre'],
    'Label': ['label', 'contact_person', 'email', 'address', 'city', 'state', 'phone', 'comment'],
    'Review': ['album', 'review'],
    'User': ['first_name', 'last_name', 'username', 'djname'],
}
LIST_FIELDS = {
    'Album': ['album', 'artist', 'label', 'genre', 'year', 'date_added', 'date_removed', 'status', 'format'],
    'Artist': DETAIL_FIELDS['Artist'],
    'Genre': DETAIL_FIELDS['Genre'],
    'Subgenre': DETAIL_FIELDS['Subgenre'],
    'Label': DETAIL_FIELDS['Label'],
    'Review': DETAIL_FIELDS['Review'],
    'User': DETAIL_FIELDS['User'],
}
SORTABLE_FIELDS = {
    'Album': DETAIL_FIELDS['Album'],
    'Artist': DETAIL_FIELDS['Artist'],
    'Genre': DETAIL_FIELDS['Genre'],
    'Subgenre': DETAIL_FIELDS['Subgenre'],
    'Label': ["label"],
    'Review': ["album", "date_added", "user"],
    'User': DETAIL_FIELDS['User'],
}


class User(AbstractUser):
    djname = models.CharField(max_length=40, null=True, blank=True)
    phone = models.CharField(max_length=80, null=True, blank=True)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        null = True,
        blank = True
    )
    date_trained = models.DateField(default=date.today, null=True)

    AUTHLEVEL_CHOICES = [
        ("none", "None"),
        ("user", "User"),
        ("exec", "Exec"),
        ("admin", "Admin"),
    ]

    auth_level = models.CharField(max_length=5, choices=AUTHLEVEL_CHOICES, default='user')

    olddb_id = models.IntegerField(null=True, blank=True)

    @property
    def reviews_this_semester(self):
        now = datetime.now()
        fall = datetime(year=now.year, month=8, day=26, hour=0, minute=0, second=0)
        spring = datetime(year=now.year, month=1, day=10, hour=0, minute=0, second=0)

        reviews = self.review_set.all()

        if now > fall:
            return reviews.filter(date_added__gt=fall).count()
        return reviews.filter(date_added__gt=spring).count()

    def get_absolute_url(self):
        return reverse('library:profile', kwargs = {'pk': self.pk})

    @property
    def name(self):
        name = ''
        if self.first_name:
            name += self.first_name + ' '
        if self.last_name:
            name += self.last_name
        if not self.first_name and not self.last_name:
            if self.djname:
                name = self.djname
            else:
                name = self.username
        return name.strip()

    @property
    def table(self):
        return "user"

    def __str__(self):
        return self.name

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
    genre = models.CharField(max_length=255, default='')
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

    class Meta:
        ordering = ('genre',)

class Subgenre(models.Model):
    subgenre = models.CharField(max_length=255, default='')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    olddb_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.subgenre

    def get_absolute_url(self):
        return reverse('library:detail', kwargs = {'table': 'subgenre', 'pk': self.pk})

    @property
    def table(self):
        return "subgenre"

    @property
    def json(self):
        return {"name": str(self),
                "id": self.id}

    class Meta:
        ordering = ('genre', 'subgenre')

class Album(models.Model):
    album = models.CharField(max_length=255, default='')
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True)
    label = models.ForeignKey(Label, on_delete=models.SET_NULL, null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    subgenre = models.ManyToManyField(Subgenre, blank=True)
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


ADDITION = 1
CHANGE = 2
DELETION = 3
ACTION_CHOICES = [
    (ADDITION, "created"),
    (CHANGE, "updated"),
    (DELETION, "deleted"),
]
class LibraryEntry(models.Model):
    """
    Library Entries track all of the actions made on the site by users
    """
    action = models.IntegerField(choices=ACTION_CHOICES, default=1)
    action_time = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    object_id = models.IntegerField(null=True, blank=True)
    object_str = models.CharField(max_length=255, null=True, blank=True)

    TABLE_CHOICES = [
        ("Album", "Album"),
        ("Artist", "Artist"),
        ("Label", "Label"),
        ("Review", "Review"),
        ("Genre", "Genre"),
        ("Subgenre", "Subgenre"),
        ("User", "User"),
    ]
    table = models.CharField(max_length=16, null=True, blank=True, choices=TABLE_CHOICES)

    changed_fields = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)

    @property
    def object(self):
        ModelClass = apps.get_model(app_label='library', model_name=self.table)
        if self.action == DELETION:
            return None
        try:
            return ModelClass.objects.get(pk=self.object_id)
        except Exception as e:
            print(e)
            return None

    def __str__(self):
        user = str(self.user) if self.user else "deleted user"
        if self.table == "Review" and self.action == ADDITION:
            return f"{user} reviewed the album {self.object_str}"
        # TODO: do something with changed_fields here
        s = f'{user} {self.get_action_display()} the {self.table} {self.object_str}'
        return s


    @classmethod
    def create_entry(cls, user, action, instance=None, table=None, **kwargs):
        object_id = kwargs.pop('object_id', instance.id if instance else None)
        table = kwargs.pop('table', instance.table.capitalize() if instance else table)
        object_str = kwargs.pop('object_str', str(instance) if instance else None)
        if instance and table == "Review":
            object_str = str(instance.album)

        entry = cls(
                table = table,
                object_id = object_id,
                object_str = object_str,
                action = action,
                user = user,
                **kwargs,
            )
        entry.save()

    class Meta:
        ordering = ('-action_time',)


"""
Save an old copy of the instance so we can compare it
to get changed fields
"""
def pre_save_handler(sender, instance, **kwargs):
    if instance.pk:
        instance._pre_save_instance = copy.deepcopy(sender.objects.get(pk=instance.pk))


# https://stackoverflow.com/a/8874383/22390568
def get_request():
    import inspect
    for frame_record in inspect.stack():
        if frame_record[3]=='get_response':
            request = frame_record[0].f_locals['request']
            return request
    else:
        request = None
        return

"""
Every time we save, create a LogEntry
"""
def post_save_handler(sender, instance, created, **kwargs):
    request = get_request()
    if not request or not request.user.is_authenticated:
        return
    # don't even make a logentry if we don't have the request

    changed_fields = None
    if created:
        action = ADDITION
    else:
        action = CHANGE
        # get changed fields
        if hasattr(instance, '_pre_save_instance'):
            old_instance = instance._pre_save_instance
            changed_fields = []
            for field in DETAIL_FIELDS[instance.table.capitalize()]:
                old_value = getattr(old_instance, field)
                new_value = getattr(instance, field)
                if getattr(old_instance, field) != getattr(instance, field):
                    changed_fields.append([field, old_value, new_value])
        if not changed_fields:
            return

    LibraryEntry.create_entry(
        user = request.user,
        action = action,
        instance = instance,
        changed_fields = changed_fields,
    )

def post_delete_handler(sender, instance, **kwargs):
    request = get_request()
    if not request or not request.user.is_authenticated:
        return
    # don't even make a logentry if we don't have the request

    LibraryEntry.create_entry(
        user = request.user,
        action = DELETION,
        instance = instance,
    )

models_to_connect = [Review, User, Genre, Subgenre, Album, Artist, Label]
for model in models_to_connect:
    pre_save.connect(pre_save_handler, sender=model)
    post_save.connect(post_save_handler, sender=model)
    post_delete.connect(post_delete_handler, sender=model)
