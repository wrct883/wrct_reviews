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
    SearchForm,
    AlbumForm,
    ArtistForm,
    LabelForm,
    GenreForm,
    SubgenreForm,
    ReviewForm,
    UserForm,
)

PAGINATION_COUNT = 25
ORDERING_SUFFIX = "_o"
def add_table(request, table_dict, queryset, param, name=None, count=PAGINATION_COUNT):
    """
    request: the WSGI request object
    table_dict: dict to add the generated, paginated/ordered queryset to
    queryset: the queryset/collection of objects to paginate/order
    param: the page parameter for the table (page, albums, etc)
    name: optional, the name to call in the template to access this table
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
        "fields": LIST_FIELDS[table],
    }

def index(request):
    review_period = datetime.now() - timedelta(days=30*3)
    reviews = Review.objects.filter(date_added__gt = review_period, date_added__lt=timezone.now())

    album_period = datetime.now() - timedelta(days=30*1)
    albums = Album.objects.filter(date_added__gt = album_period, date_added__lt=timezone.now())

    tables = {}
    add_table(request, tables, reviews, 'reviews', count=10)
    add_table(request, tables, albums, 'albums', count=10)

    context = {
        "indexView": True,
        "tables": tables,
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
    form = SearchForm()
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

    tables = {}
    add_table(request,
              table_dict = tables,
              queryset = objects,
              param = 'page',
              name = "list")

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
    if ((getattr(obj, 'album_set', False) and obj.album_set.count) or
        (getattr(obj, "review_set", False) and obj.review_set.count)):
        canDelete = False
    canDelete |= request.user.auth_level == 'admin'

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

