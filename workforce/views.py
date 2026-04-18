from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Collaborator
from .forms import CollaboratorForm


@login_required
def collaborator_list(request):
    collaborators = Collaborator.objects.select_related(
        'company', 'insurance_fund'
    ).order_by('name')
    return render(request, 'workforce/collaborator_list.html', {'collaborators': collaborators})


@login_required
def collaborator_create(request):
    form = CollaboratorForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('workforce:list')
    return render(request, 'workforce/collaborator_form.html', {'form': form, 'title': 'Novo colaborador'})


@login_required
def collaborator_update(request, pk):
    collaborator = get_object_or_404(Collaborator, pk=pk)
    form = CollaboratorForm(request.POST or None, instance=collaborator)
    if form.is_valid():
        form.save()
        return redirect('workforce:list')
    rates = collaborator.hourly_rates.order_by('-start_date')
    return render(request, 'workforce/collaborator_form.html', {
        'form': form, 'title': collaborator.name,
        'collaborator': collaborator, 'rates': rates
    })
