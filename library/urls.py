from django.urls import path, register_converter

from . import converters, views

register_converter(converters.TableConverter, "table")


app_name = 'library'
urlpatterns = [
    path("", views.index, name="index"),
    path("<table:table>/<int:pk>", views.detail, name="detail"),
]
