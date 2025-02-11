from django import forms
from .models import Resume


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title', 'category', 'about', 'education', 'vuz', 'experience', 'skills', 'phone_number', 'email', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'formkz-control'}),
            'category': forms.Select(attrs={'class': 'formkz-control'}),
            'about': forms.Textarea(attrs={'class': 'formkz-control'}),
            'education': forms.Select(attrs={'class': 'formkz-control'}),
            'vuz': forms.TextInput(attrs={'class': 'formkz-control'}),
            'experience': forms.Select(attrs={'class': 'formkz-control'}),
            'skills': forms.Textarea(attrs={'class': 'formkz-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'formkz-control'}),
            'email': forms.EmailInput(attrs={'class': 'formkz-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})