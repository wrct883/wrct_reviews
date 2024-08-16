from django.contrib.auth.models import AbstractUser
from django.db import models

from django.urls import reverse

class User(AbstractUser):
    djname = models.CharField(max_length=40, null=True)
    phone = models.CharField(max_length=80, null=True, blank=True)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        null = True,
        blank = True
    )

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
        return self.review_set.all().count()

    def get_absolute_url(self):
        return reverse('accounts:detail', kwargs = {'pk': self.pk})

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
