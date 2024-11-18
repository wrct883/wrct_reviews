from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic
from .models import (
    User, Review, Album,
    LibraryEntry,
    ADDITION, CHANGE, DELETION,
    DETAIL_FIELDS, SEARCH_FIELDS, LIST_FIELDS, SORTABLE_FIELDS,
)

from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.apps import apps
from django.db.models import Q, Count
from .forms import (
    SearchForm,# AlbumSearchForm,
    AlbumForm,
    ArtistForm,
    LabelForm,
    GenreForm,
    SubgenreForm,
    ReviewForm,
    UserForm,
    BulkModifyAlbumForm,
    BulkModifyListForm,
)
from urllib.parse import urlencode

PAGINATION_COUNT = 25
ORDERING_SUFFIX = "_o"
def add_table(request, table_dict, queryset, param, name=None, count=PAGINATION_COUNT, fields=None):
    """
    request: the WSGI request object
    table_dict: dict to add the generated, paginated/ordered queryset to
    queryset: the queryset/collection of objects to paginate/order
    param: the page parameter for the table (page, albums, etc)
    name: optional, the name to call in the template to access this table

    returns: a dictionary with key "name", and values
    * objects -> the table paginator
    * field_orders -> a dictionary  of the field and its sort direction (up arrow/down arrow)
    * param -> the page parameter for the table
    * sortable -> the list of sortable fields
    * fields -> the list of fields that should be displayed in the table
    * count -> the total number of objects in the paginator
    """
    name = name if name else param
    table = queryset.model.__name__

    ordering = request.GET.get(param + ORDERING_SUFFIX)
    field_orders = {}
    if ordering:
        try:
            order_fields = []
            for o in ordering.split("."):
                reverse = o[0] if o.startswith('-') else ''
                fname = o[1:] if o.startswith('-') else o
                if fname in ["album", "artist", "genre", "label", "subgenre"] and fname != table.lower():
                    order_fields.append(f'{reverse}{fname}__{fname}')
                else:
                    order_fields.append(o)

                field_orders[fname] = "▼" if reverse else "▲"
            queryset = queryset.order_by(*order_fields)
        except Exception as e:
            print(e)
            messages.error(request, "invalid ordering parameter")

    objects_paginator = Paginator(queryset, count)
    objects_page_number = request.GET.get(param)
    objects_paged = objects_paginator.get_page(objects_page_number)

    table_dict[name] = {
        "objects": objects_paged,
        "field_orders": field_orders,
        "param": param,
        "sortable": SORTABLE_FIELDS[table],
        "fields": fields if fields else LIST_FIELDS[table],
        'count': queryset.count(),
    }

def index(request):
    review_period = datetime.now() - timedelta(days=30*3)
    reviews = Review.objects.filter(date_added__gt = review_period, date_added__lt=timezone.now())

    album_period = datetime.now() - timedelta(days=30*1)
    albums = Album.objects.filter(date_added__gt = album_period, date_added__lt=timezone.now())

    tables = {}
    add_table(request, tables, reviews, 'reviews', count=10)
    add_table(request, tables, albums, 'albums', count=10)

    searchForm = SearchForm()

    context = {
        "indexView": True,
        "tables": tables,
        "searchForm": searchForm,
    }
    return render(request, "library/index.html", context)

def detail(request, table, pk):
    ModelClass = apps.get_model(app_label='library', model_name=table)
    obj = get_object_or_404(ModelClass, pk=pk)


    tables = {}
    if table == 'Artist' or table == 'Label':
        add_table(request, tables, obj.album_set.all(), 'album')
    elif table == "Album" or table == 'User':
        add_table(request, tables, obj.review_set.all(), 'review')
    elif table == "Genre":
        add_table(request, tables, obj.subgenre_set.all(), 'subgenre')

    context = {
        'table': table,
        'object': obj,
        'fields': DETAIL_FIELDS[table],
        'fieldsDict': DETAIL_FIELDS,

        'tables': tables,
    }
    return render(request, 'library/detail.html', context)

@login_required
def profile(request, pk=None):
    if pk is None:
        pk = request.user.id
    return detail(request, 'User', pk)

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
            if not table:
                table = 'album'
            query_params = {
                key: form.cleaned_data.get(key) for key in form.fields.keys() if (
                    key != 'table' and form.cleaned_data.get(key)
                )
            }
            if not query_params.get('query'):
                query_params.pop('pos', None)
            #pos = form.cleaned_data.get('pos')
            #query = form.cleaned_data.get('query')
            query_params = urlencode(query_params)
            url = reverse('library:list', kwargs = {'table': table})
            if query_params:
                url += '?' + query_params
            return HttpResponseRedirect(url)
        else:
            messages.error(request, "invalid search form")
            return HttpResponseRedirect(reverse('library:index'))
    elif not table:
        messages.error(request, "invalid url or method")
        return HttpResponseRedirect(reverse('library:index'))

    # we are on the list page formally now
    form = SearchForm(request.GET)
    if not form.is_valid():
        messages.error(request, 'invalid search search form')
        return HttpResponseRedirect(reverse('library:index'))

    # filter objects using the search form
    objects = form.search(table)
    isAlbumSearch = form.isAlbumSearch
    fields = [f for f in LIST_FIELDS[table]]
    if table.lower() == 'album':
        if not (query or isAlbumSearch):
            objects = objects.filter(date_removed__isnull=True)
        # ^unless you're searching for an album, do not show objects that have been
        # removed from the bin
        else:
            fields.insert(fields.index('date_added') + 1, 'date_removed')
        # add in date_removed to the list otherwise


    request.session['search_form_data'] = form.data

    tables = {}
    add_table(request,
              table_dict = tables,
              queryset = objects,
              param = 'page',
              name = "list",
              fields = fields)

    """
    need to decide if we're on an AJAX view here and then return json if so
    """
    isJsonView = "json" in request.resolver_match.view_name

    # redirect to detail page if there's only one match
    if objects.count() == 1 and not isJsonView:
        return HttpResponseRedirect(reverse("library:detail", kwargs={'table': table.lower(), 'pk': objects.first().pk}))

    if isJsonView:
        data = [obj.json for obj in tables['list']['objects']]
        return JsonResponse(data=data, safe=False)

    context = {
        "table": table,
        "form": form,
        "listView": True,
        'isAlbumSearch': isAlbumSearch,

        "tables": tables,
    }
    return render(request, 'library/list.html', context)


CREATE_FORMS = {
    'Album': AlbumForm,
    'Artist': ArtistForm,
    'Genre': GenreForm,
    'Subgenre': SubgenreForm,
    'Label': LabelForm,
    'Review': ReviewForm,
    'User': UserForm,
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


    form = CREATE_FORMS[table](data = request.POST or None, related=related, related_obj=related_obj, instance=obj, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            obj = form.save(commit=False)
            if getattr(obj, 'user', None) is None:
                obj.user = request.user
            if table.lower() in ['album', 'review'] and not obj.date_added:
                obj.date_added = timezone.now().date()
            obj.save()
            form.save_m2m()
            verb = 'created' if not pk else 'updated'
            messages.success(request, f"{obj.table} {verb} successfully")

            if table == 'Subgenre' and related == 'Album':
                related_obj.subgenre.add(obj)
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
    if ((getattr(obj, 'album_set', False) and obj.album_set.count()) or
        (getattr(obj, "review_set", False) and obj.review_set.count())):
        canDelete = False
    canDelete |= request.user.auth_level.lower() == 'admin'

    #form = CREATE_FORMS[table](data = request.POST or None, related = related, related_obj = related_obj)
    if request.method == 'POST':
        if canDelete:
            table = obj.table
            object_id = obj.id
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


'''
Return a dictionary of fields and their respective values
Asser that all albums in `albums` have the same value for these fields
'''
def get_shared_fields(albums):
    values = albums.values()
    shared_values = values[0]
    distinct_keys = set()
    for v in values:
        for key, value in v.items():
            if key in distinct_keys:
                continue
            if shared_values.get(key) != value:
                shared_values.pop(key)
                distinct_keys.add(key)
    if shared_values.get('genre_id'):
        shared_values['genre'] = shared_values.pop('genre_id')
    return shared_values
'''
Bulk modify is currently only supported for albums
I have no idea why you want to have bulk modification for anything execpt for albums
But like, if you do, then I leave generalizing this code as an exercise for the reader
'''
@login_required
def bulk_modify(request):
    def get_albums():
        album_data = request.session.get('bulk_modify_data')
        search_data = request.session.get('search_form_data')
        if not album_data:
            messages.error(request, 'invalid session')
            return HttpResponseRedirect(reverse('library:list', kwargs={"table": table}))
        listForm = BulkModifyListForm(album_data)
        return listForm.get_albums(search_data)

    table = 'album'
    if not request.user.canBulkModify:
        messages.error(request, "you do not have permission to perform this action")
        return HttpResponseRedirect(reverse('library:list', kwargs={"table": table}))
    albums = Album.objects.none()
    '''
    If you're making a post request, coming from the search view
    Or if you're makinga  get request, coming from the search view
    display the form to modify the albums
    '''
    if ((request.method == "POST" and 'bulk-modify-list' in request.POST) or
        (request.method == "GET" and request.session.get('bulk_modify_data'))):
        data = request.POST if request.method == "POST" else request.session.get('bulk_modify_data')
        listForm = BulkModifyListForm(request.POST)
        if not listForm.is_valid():
            messages.error(request, "your selection was invalid (???)")
            return HttpResponseRedirect(reverse('library:list', kwargs={"table": table}))
        search_data = request.session.get('search_form_data')
        albums = listForm.get_albums(search_data)
        '''
        set the form to show fields that have the same value
        '''
        shared_fields = get_shared_fields(albums)

        form = BulkModifyAlbumForm(initial=shared_fields)
        request.session['bulk_modify_data'] = listForm.cleaned_data
    elif request.method == "POST":
        '''
        If you're making a POST request to modify the albums...
        '''
        print(request.POST)
        if 'bulk-modify' in request.POST:
            albums = get_albums()
            shared_fields = get_shared_fields(albums)
            form = BulkModifyAlbumForm(request.POST)
            if form.is_valid():
                ## successfully submitted form, now we're ready to update data
                non_empty_fields = {key: value for key, value in form.cleaned_data.items() if value}
                ## remove all entries form non_emtpy_fields that have the same value as a shared_field
                for key, value in shared_fields.items():
                    if non_empty_fields.get(key) == value:
                        non_empty_fields.pop(key, None)

                ## update remaining values in albums
                ## if an album was in the bin, but is now OOB, update that...
                if non_empty_fields:
                    for album in albums:
                        original_status = album.status
                        for key, value in non_empty_fields.items():
                            if key == 'subgenre': # set m2m manually
                                album.subgenre.clear()
                                album.subgenre.set(value)
                            else:
                                setattr(album, key, value)
                        album.save()
                messages.success(request, "successfully modified albums")
            else:
                messages.error(request, 'invalid form fields')
                return HttpResponseRedirect(reverse('library:bulk_modify'))
        '''
        If you're making a POST request to delete the albums...
        '''
        if 'delete' in request.POST:
            albums = get_albums()
            if albums.count() > 5000:
                messages.error(request, "this website won't let you delete > 5000 albums at once in one go, bc otherwise that's probably a mistake...")
                return HttpResponseRedirect(reverse('library:bulk_modify'))
            else:
                albums.delete()
                messages.success(request, "successfully deleted albums")
        return HttpResponseRedirect(reverse('library:list', kwargs={"table": table}))

    else:
        messages.error(request, "invalid session, are you supposed to be editing this right now?")
        return HttpResponseRedirect(reverse('library:list', kwargs={"table": table}))
    context = {
        'table': table,
        'form': form,
        'listForm': listForm,
        'albums': albums,
        'count': albums.count(),
    }
    return render(request, 'library/bulk_modify.html', context)


class ActionListView(generic.list.ListView):
    model = LibraryEntry
    paginate_by = 100
    template_name = 'library/actions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ADDITION"] = ADDITION
        context["DELETION"] = DELETION
        context["CHANGE"] = CHANGE
        context["actionView"] = True
        return context

def leaderboard(request):
    users = User.objects.all().annotate(review_count=Count("review")).order_by("-review_count")
    thisSemester = []
    for user in users:
        count = user.reviews_this_semester
        if count:
            thisSemester.append((user, count))
    thisSemester = sorted(thisSemester, key=lambda x: x[1], reverse=True)
    context = {
        "users": users,
        "this_semester": thisSemester,
        "leaderboardView": True,
    }
    return render(request, 'library/leaderboard.html', context)

