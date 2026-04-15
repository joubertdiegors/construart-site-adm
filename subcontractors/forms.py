from django import forms
from .models import Subcontractor


class SubcontractorForm(forms.ModelForm):
    class Meta:
        model = Subcontractor
        fields = '__all__'