from django import forms
from users.forms import UserProfileForm
from users.models import *
from django.forms import inlineformset_factory
from django.forms import ModelForm


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number', 'email']



UserProfileFormSet = inlineformset_factory(User, UserProfile, form=UserProfileForm, extra=1, can_delete=False)
