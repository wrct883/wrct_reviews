from django.contrib.auth.models import AbstractUser
from django.db import models

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

