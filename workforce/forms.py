from django import forms

from .models import Collaborator


class CollaboratorForm(forms.ModelForm):
    class Meta:
        model = Collaborator
        fields = ['company', 'insurance_fund', 'name', 'role', 'phone', 'email', 'status', 'notes']
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'insurance_fund': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
