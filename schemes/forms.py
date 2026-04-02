from django import forms
from .models import Scheme

W = {'class': 'form-control'}


class SchemeForm(forms.ModelForm):
    class Meta:
        model = Scheme
        fields = ['title', 'reference_number', 'content', 'document', 'is_published', 'requires_signature']
        widgets = {
            'title': forms.TextInput(attrs=W),
            'reference_number': forms.TextInput(attrs=W),
            'content': forms.Textarea(attrs={**W, 'rows': 15, 'id': 'scheme-content'}),
        }
