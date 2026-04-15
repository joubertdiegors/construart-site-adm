from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django import forms
from .models import Client, ClientAddress, ClientContact


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'trade_name', 'category', 'legal_form',
                  'vat_number', 'vat_rate', 'responsible', 'notes', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'trade_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'legal_form': forms.Select(attrs={'class': 'form-control'}),
            'vat_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'responsible': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


@login_required
def client_list(request):
    clients = Client.objects.prefetch_related('addresses', 'contacts').order_by('name')
    return render(request, 'clients/client_list.html', {'clients': clients})


@login_required
def client_create(request):
    form = ClientForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('clients:list')
    return render(request, 'clients/client_form.html', {'form': form, 'title': 'Novo cliente'})


@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=client)
    if form.is_valid():
        form.save()
        return redirect('clients:list')
    return render(request, 'clients/client_form.html', {'form': form, 'title': client.name, 'client': client})


@login_required
def client_detail(request, pk):
    client = get_object_or_404(
        Client.objects.prefetch_related('addresses', 'contacts', 'projects'), pk=pk
    )
    return render(request, 'clients/client_detail.html', {'client': client})