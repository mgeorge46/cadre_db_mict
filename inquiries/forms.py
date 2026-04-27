from django import forms
from .models import Inquiry, InquiryResponse, InquiryCategory

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
            'category': forms.Select(attrs=WS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = InquiryCategory.objects.filter(is_active=True)
        self.fields['category'].empty_label = '-- Select Category --'
        self.fields['category'].required = False


class InquiryCategoryForm(forms.ModelForm):
    class Meta:
        model = InquiryCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs=W),
            'description': forms.Textarea(attrs={**W, 'rows': 3}),
        }


class InquiryResponseForm(forms.ModelForm):
    class Meta:
        model = InquiryResponse
        fields = ['message', 'is_internal']
        widgets = {
            'message': forms.Textarea(attrs={**W, 'rows': 4, 'placeholder': 'Type your response here...'}),
        }
