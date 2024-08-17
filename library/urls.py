from django.urls import path, register_converter

from . import converters, views

register_converter(converters.TableConverter, "table")


app_name = 'library'
urlpatterns = [
    path("", views.index, name="index"),
    path("<table:table>/<int:pk>", views.detail, name="detail"),
    path("search", views.list, name="search"),
    path("search/<table:table>", views.list, name="search_json"),
    path("<table:table>", views.list, name="list"),
    path("<table:table>s", views.list, name="list"),
    path("<table:table>/create", views.create, name="create"),
    path("<table:related>/<int:related_pk>/create/<table:table>", views.create, name="create"),
    path("<table:table>/<int:pk>/delete", views.delete, name="delete"),
    path("<table:table>/<int:pk>/update", views.create, name="update"),

    path("accounts/profile", views.profile, name="profile"),
    path("accounts/profile/<int:pk>", views.profile, name="profile"),

    path("actions", views.ActionListView.as_view(), name="actions"),
    path("leaderboard", views.leaderboard, name="leaderboard"),
]
