from django import forms
from .models import Subcontractor


class SubcontractorForm(forms.ModelForm):
    class Meta:
        model = Subcontractor
        fields = ['name', 'vat_number', 'contact_name', 'phone', 'email', 'address', 'status', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_number': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }