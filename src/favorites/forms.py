from django import forms

class FavoriteSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'formkz-control',
            'placeholder': 'Поиск по названию вакансии'
        })
    )