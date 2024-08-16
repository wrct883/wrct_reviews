from django import forms
from django.db import models

from .models import (
    Album,
    Artist,
    Label,
    Genre,
    Subgenre,
    Review,
    User,
)


# TODO: make this a constant with converters and views.py
TABLE_CHOICES = [('album', 'Album'), ('artist', 'Artist'), ('genre', 'Genre'), ('label', 'Label'), ('review', 'Review'), ('user', 'User')]
POS_CHOICES = [('icontains', 'include'), ('istartswith', 'start with'), ('iendswith', 'end with'), ('iexact', 'match exactly')]
class SearchForm(forms.Form):
    table = forms.ChoiceField(choices=TABLE_CHOICES)
    pos = forms.ChoiceField(choices=POS_CHOICES)
    query = forms.CharField(required=False)


class CustomSelectWidget(forms.Select):
    template_name = 'library/select.html'  # Optionally, create a custom template for your widget

    def __init__(self, field_name, selected=None, instance=None):
        # TODO:
        # use the field name, get all possible valid options
        if instance and getattr(instance, field_name):
            initial = getattr(instance, field_name)
            super().__init__(choices = [(initial.id, str(initial))])
            return
        if selected:
            super().__init__(choices = [(selected.id, str(selected))])
            return
        super().__init__()

class LibraryCreateFormMixin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        related = kwargs.pop('related')
        related_obj = kwargs.pop('related_obj')
        super().__init__(*args, **kwargs)

        ## custom excluded fields
        for field_name in ['user', 'date_added', 'date_removed', 'olddb_id']:
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
                print('TODO', field, field.__dict__)


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
        fields = ('first_name', 'last_name', 'djname', 'phone', 'email', 'auth_level')
