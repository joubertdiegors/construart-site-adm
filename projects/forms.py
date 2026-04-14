from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Project

from clients.models import ClientContact


class ProjectForm(forms.ModelForm):

    start_date = forms.DateField(
        label=_("Start date"),
        widget=forms.DateInput(
            attrs={'type': 'date'},
            format='%Y-%m-%d'
        ),
        input_formats=['%Y-%m-%d'],
        required=False
    )

    end_date = forms.DateField(
        label=_("End date"),
        widget=forms.DateInput(
            attrs={'type': 'date'},
            format='%Y-%m-%d'
        ),
        input_formats=['%Y-%m-%d'],
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'name',
            'client',
            'contacts',
            'address',
            'managers',
            'start_date',
            'end_date',
            'notes',
            'has_work_registration',
            'work_registration_type',
            'work_registration_number',
        ]

        widgets = {
            'contacts': forms.SelectMultiple(attrs={'size': 6}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        has_registration = cleaned_data.get('has_work_registration')
        reg_type = cleaned_data.get('work_registration_type')
        reg_number = cleaned_data.get('work_registration_number')

        # 🔥 REGRA 1 — Datas válidas
        if start_date and end_date:
            if end_date < start_date:
                self.add_error('end_date', _("End date cannot be before start date."))

        # 🔥 REGRA 2 — Registro obrigatório
        if has_registration:
            if not reg_type:
                self.add_error('work_registration_type', _("Select a registration type."))
            if not reg_number:
                self.add_error('work_registration_number', _("Enter the registration number."))

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔥 CASO 1: POST (quando usuário envia o form)
        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['contacts'].queryset = ClientContact.objects.filter(client_id=client_id)
            except:
                self.fields['contacts'].queryset = ClientContact.objects.none()

        # 🔥 CASO 2: EDIÇÃO (instance já existe)
        elif self.instance.pk and self.instance.client:
            self.fields['contacts'].queryset = self.instance.client.contacts.all()

        # 🔥 CASO 3: CREATE (sem POST ainda)
        else:
            self.fields['contacts'].queryset = ClientContact.objects.all()