from django.shortcuts import render, get_object_or_404, redirect
from .models import Subcontractor
from .forms import SubcontractorForm


def subcontractor_list(request):
    subcontractors = Subcontractor.objects.all()
    return render(request, 'subcontractors/list.html', {
        'subcontractors': subcontractors
    })


def subcontractor_create(request):
    form = SubcontractorForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('subcontractors:list')

    return render(request, 'subcontractors/form.html', {
        'form': form
    })


def subcontractor_update(request, pk):
    subcontractor = get_object_or_404(Subcontractor, pk=pk)
    form = SubcontractorForm(request.POST or None, instance=subcontractor)

    if form.is_valid():
        form.save()
        return redirect('subcontractors:list')

    return render(request, 'subcontractors/form.html', {
        'form': form
    })