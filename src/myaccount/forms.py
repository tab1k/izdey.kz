from django import forms
from jobs.models import JobResponse


class JobResponseStatusForm(forms.ModelForm):
    class Meta:
        model = JobResponse
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget = forms.Select(choices=JobResponse.STATUS_CHOICES)
