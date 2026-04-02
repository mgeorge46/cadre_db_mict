from django import forms
from .models import Announcement

W = {'class': 'form-control'}
WS = {'class': 'form-select'}


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        # target_entity_type and target_entity_ids handled manually in views/templates
        fields = ['title', 'content', 'is_published', 'expiry_date',
                  'filter_type', 'send_email', 'requires_acknowledgment']
        widgets = {
            'title': forms.TextInput(attrs=W),
            'content': forms.Textarea(attrs={**W, 'rows': 10}),
            'expiry_date': forms.DateInput(attrs={**W, 'type': 'date'}),
            'filter_type': forms.Select(attrs=WS),
        }
