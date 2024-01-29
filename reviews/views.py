from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from .models import Review

class IndexView(generic.ListView):
    template_name = "reviews/index.html"
    context_object_name = "reviews"
    paginate_by = 20


    def get_queryset(self):
        return Review.objects.order_by("-date_added")
