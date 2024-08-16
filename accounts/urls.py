from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path("profile", views.detail, name="profile"),
    path("profile/<int:pk>", views.detail, name="detail"),
]
