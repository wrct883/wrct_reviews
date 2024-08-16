from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic
from .models import Album, Artist, Label, Genre, Review

from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.apps import apps
from django.db.models import Q
from .forms import (
    SearchForm,
    AlbumForm,
    ArtistForm,
    LabelForm,
    GenreForm,
    ReviewForm
)

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
        'User': ('first_name', 'last_name', 'djname', 'phone', 'email', 'auth_level'),
}
def detail(request, table, pk):
    ModelClass = apps.get_model(app_label='library', model_name=table)
    obj = get_object_or_404(ModelClass, pk=pk)
    context = {
        'table': table,
        'object': obj,
        'fields': DETAIL_FIELDS[table],
        'fieldsDict': DETAIL_FIELDS,
    }
    return render(request, 'library/detail.html', context)

SEARCH_FIELDS = {
    'Album': ['album', 'artist'],
    'Artist': ['artist', 'short_name'],
    'Genre': ['genre'],
    'Label': ['label', 'contact_person', 'email', 'address', 'city', 'state', 'phone', 'comment'],
    'Review': ['album', 'review'],
}
def list(request, table = None):
    """
    Produces a list of objects either from a search form, or from a url
    If the request is a post, it means the user submitted a search form
        in that case, parse form info and redirect to the correct url
    Otherwise, request is just a GET
    Given the table, produce paginated results with the specific filter
    """
    # The user is searching
    query = None
    pos = None
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            table = form.cleaned_data.get('table')
            pos = form.cleaned_data.get('pos')
            query = form.cleaned_data.get('query')
            url = reverse('library:list', kwargs = {'table': table})
            if query:
                url += f"?pos={pos}&query={query}"
            return HttpResponseRedirect(url)
        else:
            messages.error(request, "invalid search form")
            return HttpResponseRedirect(reverse('library:index'))
    elif not table:
        messages.error(request, "invalid url or method")
        return HttpResponseRedirect(reverse('library:index'))

    # we are on the list page formally now
    ModelClass = apps.get_model(app_label='library', model_name=table)
    objects = ModelClass.objects.all()

    # filter objects if we have a query
    query = request.GET.get('query')
    pos = request.GET.get('pos')
    if query:
        q_objects = Q()  # Initialize an empty Q object
        for field in SEARCH_FIELDS[table]:
            isForeignKey = ModelClass._meta.get_field(field).get_internal_type() == 'ForeignKey'
            #isForeignKey = isinstance(ModelClass._meta.get_field('field'), ForeignKey)
            q_objects |= Q(**{f"{field}{f'__{field}' if isForeignKey else ''}__{pos}": query})
        objects = objects.filter(q_objects)

    """
    need to decide if we're on an AJAX view here and then return json if so
    """
    isJsonView = "json" in request.resolver_match.view_name
    #isJsonView = request.headers.get("x-requested-with") == "XMLHttpRequest"

    # redirect to detail page if there's only one match
    if objects.count() == 1 and not isJsonView:
        return HttpResponseRedirect(reverse("library:detail", kwargs={'table': table.lower(), 'pk': objects.first().pk}))

    objects_paginator = Paginator(objects, 25)
    objects_page_number = request.GET.get("page")
    objects_paged = objects_paginator.get_page(objects_page_number)

    if isJsonView:
        data = [obj.json for obj in objects_paged]
        return JsonResponse(data=data, safe=False)

    context = {
        "table": table,
        "objects": objects_paged,
        "fields": DETAIL_FIELDS[table],
    }
    return render(request, 'library/list.html', context)


CREATE_FORMS = {
    'Album': AlbumForm,
    'Artist': ArtistForm,
    'Genre': GenreForm,
    'Label': LabelForm,
    'Review': ReviewForm,
}
@login_required
def create(request, table, related=None, related_pk=None, pk=None):
    """
    allows you to create an object of the type <table>
    <related> corresponds to an object that gets related to the new object

    so if table is "album", and related is "artist", then that album's artist
    is going to be set to whatever the pk is
    """
    ModelClass = apps.get_model(app_label='library', model_name=table)

    related_obj = None
    if related and related_pk:
        RelatedModelClass = apps.get_model(app_label='library', model_name=related)
        related_obj = get_object_or_404(RelatedModelClass, pk=related_pk)

    obj = None
    if pk:
        obj = get_object_or_404(ModelClass, pk=pk)


    form = CREATE_FORMS[table](data = request.POST or None, related=related, related_obj=related_obj, instance=obj)
    if request.method == 'POST':
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.date_added = timezone.now().date()
            obj.save()
            form.save_m2m()
            verb = 'created' if not pk else 'updated'
            messages.success(request, f"{obj.table} {verb} successfully")
            return HttpResponseRedirect(obj.get_absolute_url())

    context = {
        "table": table,
        "object": obj,
        "form": form,
        "related": related_obj,
    }
    return render(request, 'library/create.html', context)

@login_required
def delete(request, table, pk):
    """
    Auth levels:
    If an artist/label/genre has any albums, don't allow delete unless user is admin
    If an album has any reviews, don't allow delete unless user is admin
    """
    ModelClass = apps.get_model(app_label='library', model_name=table)
    obj = get_object_or_404(ModelClass, pk=pk)

    canDelete = True
    if ((getattr(obj, 'album_set', False) and obj.album_set.count) or
        (getattr(obj, "review_set", False) and obj.review_set.count)):
        canDelete = False
    canDelete |= request.user.auth_level == 'admin'

    #form = CREATE_FORMS[table](data = request.POST or None, related = related, related_obj = related_obj)
    if request.method == 'POST':
        if canDelete:
            obj.delete()
            messages.success(request, f"{table} deleted successfully")
        else:
            messages.error(request, "you do not have permission to perform this action")
        return HttpResponseRedirect(reverse('library:list', kwargs={"table": table}))

    context = {
        "table": table,
        "object": obj,
        "canDelete": canDelete,
    }
    return render(request, 'library/delete.html', context)
