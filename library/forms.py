from django import forms
from django.db import models
import datetime

from .models import (
    Album, STATUS_CHOICES,
    Artist,
    Label,
    Genre,
    Subgenre,
    Review,
    User,
)

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
    end_date = forms.DateField(initial=datetime.date.today, required=False, widget=DateInput)
    status = forms.ChoiceField(choices=[('', 'Any status')] + STATUS_CHOICES, required=False)
    genre = forms.ChoiceField(choices=genreChoices, required=False)

    def clean(self):
        query = self.cleaned_data['query']
        pos = self.cleaned_data['pos']
        if query and not pos:
            raise ValidationError('query provided but not pos')

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
        related = kwargs.pop('related')
        related_obj = kwargs.pop('related_obj')
        super().__init__(*args, **kwargs)

        ## custom excluded fields
        excluded_fields = ['user', 'date_added', 'olddb_id', 'short_name']
        if not self.instance.id: # remove date_removed if you're creating a new entry
            excluded_fields.append('date_removed')
        for field_name in excluded_fields:
            if field_name in self.fields:
                self.fields.pop(field_name)

        ## Use custom select widget for all foreign key related objects
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field_obj = self._meta.model._meta.get_field(field_name)
                if isinstance(field_obj, models.ForeignKey) and field._queryset.count() > 100:
                    selected = related_obj if related and related.lower() == field_name else None
                    field.widget = CustomSelectWidget(field_name, selected=selected, instance=self.instance)

                if field_name == 'subgenre':
                    field.widget = CustomSubgenreWidget(queryset=field._queryset)

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

class UserForm(LibraryCreateFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'djname', 'phone', 'email', 'auth_level')
