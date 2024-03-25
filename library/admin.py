from django.contrib import admin
from .models import *

admin.site.register(Artist)
admin.site.register(Label)
admin.site.register(Genre)

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("album", "label", "artist", 'format', "year", "date_added", "date_removed", "status")
    raw_id_fields = ['label', 'artist']
    search_fields = ['album'] 

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "date_added", "album")
    raw_id_fields = ['user', 'album']
