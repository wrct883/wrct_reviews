from django import forms
from django.db import models
from datetime import datetime, timedelta, date
import json

from .models import (
    Album, STATUS_CHOICES,
    Artist,
    Label,
    Genre,
    Subgenre,
    Review,
    User,
    SEARCH_FIELDS,
)

from django.apps import apps
from django.db.models import Q


def genreChoices():
    return [('', 'Any genre')] + [(genre.id, genre.genre) for genre in Genre.objects.all().order_by('genre')]

class DateInput(forms.DateInput):
    input_type = 'date'

# TODO: make this a constant with converters and views.py
TABLE_CHOICES = [('album', 'Albums'), ('artist', 'Artists'), ('label', 'Labels'), ('review', 'Reviews'), ('genre', 'Genres'), ('user', 'Users')]
POS_CHOICES = [('icontains', 'include'), ('istartswith', 'start with'), ('iendswith', 'end with'), ('iexact', 'match exactly')]
class SearchForm(forms.Form):
    table = forms.ChoiceField(choices=TABLE_CHOICES, required=False)
    pos = forms.ChoiceField(choices=POS_CHOICES, required=False)
    query = forms.CharField(required=False)

    # album search forms
    start_date = forms.DateField(required=False, widget=DateInput)
    end_date = forms.DateField(initial=date.today, required=False, widget=DateInput)
    status = forms.ChoiceField(choices=[('', 'Any status')] + STATUS_CHOICES, required=False)
    genre = forms.ChoiceField(choices=genreChoices, required=False)

    def clean(self):
        query = self.cleaned_data['query']
        pos = self.cleaned_data['pos']
        if query and not pos:
            raise ValidationError('query provided but not pos')

    def search(self, table):
        valid = self.is_valid()

        ModelClass = apps.get_model(app_label='library', model_name=table)
        objects = ModelClass.objects.all()

        # filter objects if we have a query
        query = self.cleaned_data['query']
        pos = self.cleaned_data['pos']
        if query:
            q_objects = Q()  # Initialize an empty Q object
            for field in SEARCH_FIELDS[table]:
                isForeignKey = ModelClass._meta.get_field(field).get_internal_type() == 'ForeignKey'
                #isForeignKey = isinstance(ModelClass._meta.get_field('field'), ForeignKey)
                q_objects |= Q(**{f"{field}{f'__{field}' if isForeignKey else ''}__{pos}": query})
            objects = objects.filter(q_objects)

        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        genre = self.cleaned_data.get('genre')
        status = self.cleaned_data.get('status')

        if start_date:
            objects = objects.filter(date_added__gte=start_date)
        if end_date:
            objects = objects.filter(date_added__lte=end_date)
        if genre:
            objects = objects.filter(genre=genre)
        if status:
            objects = objects.filter(status=status)
        return objects

    def isAlbumSearch(self):
        start_date_str = self.cleaned_data.get('start_date')
        end_date_str = self.cleaned_data.get('end_date')
        genre = self.cleaned_data.get('genre')
        status = self.cleaned_data.get('status')

        return bool(start_date_str or end_date_str or genre or status)


class CustomSelectWidget(forms.Select):
    template_name = 'library/forms/select.html'

    def __init__(self, field_name, selected=None, instance=None):
        if instance and getattr(instance, field_name):
            initial = getattr(instance, field_name)
            super().__init__(choices = [(initial.id, str(initial))])
            return
        if selected:
            super().__init__(choices = [(selected.id, str(selected))])
            return
        super().__init__()

class CustomSubgenreWidget(forms.CheckboxSelectMultiple):
    template_name = 'library/forms/subgenre.html'

    def __init__(self, queryset):
        choices = [(obj.id, obj) for obj in queryset]
        super().__init__(choices = choices)

class LibraryCreateFormMixin(forms.ModelForm):
    error_css_class = "error no-contents"

    def __init__(self, *args, **kwargs):
        related = kwargs.pop('related', None)
        related_obj = kwargs.pop('related_obj', None)
        user = kwargs.pop('user', None)
        included_fields = kwargs.pop('included_fields', [])
        super().__init__(*args, **kwargs)

        ## custom excluded fields
        excluded_fields = set(['user', 'date_added', 'olddb_id', 'short_name'])
        if not self.instance.id: # remove date_removed if you're creating a new entry
            excluded_fields.add('date_removed')
        [excluded_fields.remove(field_name) for field_name in included_fields if field_name in excluded_fields]
        for field_name in excluded_fields:
            if field_name in self.fields:
                self.fields.pop(field_name)

        ## Use custom select widget for all foreign key related objects
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field_obj = self._meta.model._meta.get_field(field_name)
                if isinstance(field_obj, models.ForeignKey) and field._queryset.count() > 100:
                    selected = related_obj if related and related.lower() == field_name else None
                    if field_name == 'user' and user and not self.instance.user:
                        self.instance.user = user
                    field.widget = CustomSelectWidget(field_name, selected=selected, instance=self.instance)

                if field_name == 'subgenre':
                    field.widget = CustomSubgenreWidget(queryset=field._queryset)

                if field_name == 'user' and user:
                    field.initial = user.id

            elif isinstance(field, forms.fields.DateField):
               field.widget = forms.widgets.DateInput(attrs={'type': 'date'})


"""
So this feels like code duplication but django doesn't let you dynamically set what model you use :(
"""
class AlbumForm(LibraryCreateFormMixin, forms.ModelForm):
    class Meta:
        model = Album
        fields = '__all__'
        widgets = {
            #"genre": forms.Select,
            "subgenre": forms.CheckboxSelectMultiple,
        }

class ArtistForm(LibraryCreateFormMixin, forms.ModelForm):
    class Meta:
        model = Artist
        fields = '__all__'

class LabelForm(LibraryCreateFormMixin, forms.ModelForm):
    class Meta:
        model = Label
        fields = '__all__'

class GenreForm(LibraryCreateFormMixin, forms.ModelForm):
    class Meta:
        model = Genre
        fields = '__all__'

class SubgenreForm(LibraryCreateFormMixin, forms.ModelForm):
    class Meta:
        model = Subgenre
        fields = '__all__'

class ReviewForm(LibraryCreateFormMixin, forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'
        widgets = {
            'riyl': forms.Textarea(attrs={'rows': 3}),
            'instrumental': forms.Textarea(attrs={'rows': 3}),
            'recommended': forms.Textarea(attrs={'rows': 3}),
        }

    '''
    Exec can change the user for someone's review
    Useful for Internal Music
    '''
    def __init__(self, *args, **kwargs):
        user = kwargs.get('user', None)
        if user and user.canBulkModify:
            kwargs['included_fields'] = ['user']
        super().__init__(*args, **kwargs)

class UserForm(LibraryCreateFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'djname', 'phone', 'email', 'auth_level')

class BulkModifyAlbumForm(LibraryCreateFormMixin, forms.ModelForm):
    class Meta:
        model = Album
        exclude = ('album',)
        widgets = {
            "subgenre": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = False


def clean_list(value):
    if isinstance(value, list):
        try:
            return [int(v) for v in value]
        except:
            raise forms.ValidationError(f'invalid entry for list, not all integers')
    try:
        #value = [Album.objects.get(pk=albumId) for albumId in json.loads(value)]
        value = json.loads(value)
        return value
    except:
        raise forms.ValidationError(f'invalid entry for list, cannot read json')

'''
I will admit that this is bad coding practice, I'm kind of just outsourcing a function to a form, and then not really using the form, but it does the job

the job: given the information selectAll, selected (album id array), excluded (album id array), return a list of albums that the bulk modify form should process
'''
class BulkModifyListForm(forms.Form):
    selectAll = forms.BooleanField(required=False)
    selected = forms.ModelMultipleChoiceField(
        queryset=Album.objects.all(),
    )
    excluded = forms.ModelMultipleChoiceField(
        queryset=Album.objects.all(),
    )

    def is_valid(self):
        valid = super().is_valid()
        return True

    def clean(self):
        cleaned_data = super().clean()
        selected = self.data.get('selected', '[]')
        excluded = self.data.get('excluded', '[]')

        cleaned_data['selected'] = clean_list(selected)
        cleaned_data['excluded'] = clean_list(excluded)
        self.cleaned_data = cleaned_data

        return cleaned_data

    def get_albums(self, search_data):
        valid = self.is_valid()
        self.clean()
        albums = Album.objects.all()
        if search_data:
            form = SearchForm(search_data)
            albums = form.search('Album')
        if self.cleaned_data['selectAll']:
            albums = albums.exclude(pk__in=self.cleaned_data['excluded'])
        else:
            albums = albums.filter(pk__in=self.cleaned_data['selected'])
        return albums
