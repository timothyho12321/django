# forms.py
from django import forms
from .models import Note

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'file']