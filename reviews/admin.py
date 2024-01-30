from django.contrib import admin
from .models import *

admin.site.register(Artist)
admin.site.register(Label)
admin.site.register(Genre)
admin.site.register(Review)

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("album", "label", "artist", "year", "date_added", "status")
