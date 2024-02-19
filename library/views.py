from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Album, Artist, Label, Genre, Review

from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator

from django.apps import apps

def do_url_params(request, context, queryset, param):
    ordering = request.GET.get(param)
    if ordering:
        field_name = ordering if ordering[0] != '-' else ordering[1:]
        queryset = queryset.order_by(ordering).filter(**{f'{field_name}__isnull': False})
        context[param] = ordering
    return queryset

def index(request):
    context = {}
    review_period = datetime.now() - timedelta(days=30*3)
    reviews = Review.objects.filter(date_added__gt = review_period, date_added__lt=timezone.now())
    reviews = do_url_params(request, context, reviews, 'ro')

    reviews_paginator = Paginator(reviews, 10)
    reviews_page_number = request.GET.get("rpage")
    reviews_paged = reviews_paginator.get_page(reviews_page_number)
    context['reviews'] = reviews_paged

    album_period = datetime.now() - timedelta(days=30*1)
    albums = Album.objects.filter(date_added__gt = album_period, date_added__lt=timezone.now())
    albums = do_url_params(request, context, albums, 'ao')

    albums_paginator = Paginator(albums, 10)
    albums_page_number = request.GET.get("apage")
    albums_paged = albums_paginator.get_page(albums_page_number)
    context['albums'] = albums_paged

    return render(request, "library/index.html", context)

DETAIL_FIELDS = {
        'Album': ('artist', 'album', 'label', 'genre', 'year', 'date_added', 'date_removed', 'status', 'format'),
        'Artist': ('artist', 'short_name', 'comment'),
        'Genre': ('genre'),
        'Label': ('label', 'contact_person', 'email', 'address', 'city', 'state', 'phone', 'comment'),
        'Review': ('user', 'date_added', 'album', 'review'),
}
def detail(request, table, pk):
    ModelClass = apps.get_model(app_label='library', model_name=table)
    if ModelClass is None:
        message.error("huh? this shouldn't have happened...")
        return HttpResponseRedirect(reverse('library:index'))
    obj = get_object_or_404(ModelClass, pk=pk)
    context = {
        'table': table,
        'object': obj,
        'fields': DETAIL_FIELDS[table],
    }
    return render(request, 'library/detail.html', context)
