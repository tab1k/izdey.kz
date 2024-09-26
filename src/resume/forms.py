from django import forms
from .models import Resume


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title', 'category', 'about', 'education', 'vuz', 'experience', 'skills', 'phone_number', 'email', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control'}),
            'education': forms.Select(attrs={'class': 'form-control'}),
            'vuz': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.Select(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})