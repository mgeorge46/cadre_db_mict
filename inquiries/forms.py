from django import forms
from .models import Inquiry, InquiryResponse

W = {'class': 'form-control'}
WS = {'class': 'form-select'}


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['title', 'description', 'priority', 'category']
        widgets = {
            'title': forms.TextInput(attrs=W),
            'description': forms.Textarea(attrs={**W, 'rows': 6}),
            'priority': forms.Select(attrs=WS),
            'category': forms.TextInput(attrs=W),
        }


class InquiryResponseForm(forms.ModelForm):
    class Meta:
        model = InquiryResponse
        fields = ['message', 'is_internal']
        widgets = {
            'message': forms.Textarea(attrs={**W, 'rows': 4, 'placeholder': 'Type your response here...'}),
        }
