from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import Planning, PlanningWorker, PlanningSubcontractor
from projects.models import Project
from workforce.models import Collaborator
from subcontractors.models import Subcontractor


@login_required
def planning_list(request):
    projects = Project.objects.filter(
        status__in=['planning', 'active']
    ).order_by('name')

    selected_project_id = request.GET.get('project')
    selected_project = None
    plannings = []

    if selected_project_id:
        selected_project = get_object_or_404(Project, pk=selected_project_id)
        plannings = Planning.objects.filter(
            project=selected_project
        ).prefetch_related(
            'planning_workers__worker',
            'planning_workers__subcontractor',
            'planning_subcontractors__subcontractor',
        ).order_by('-date')

    return render(request, 'planning/planning_list.html', {
        'projects': projects,
        'selected_project': selected_project,
        'plannings': plannings,
    })


@login_required
def planning_detail(request, pk):
    planning = get_object_or_404(
        Planning.objects.prefetch_related(
            'planning_workers__worker',
            'planning_workers__subcontractor',
            'planning_subcontractors__subcontractor',
        ),
        pk=pk
    )
    collaborators = Collaborator.objects.filter(
        company__status='active'
    ).select_related('company').order_by('name')
    subcontractors = Subcontractor.objects.filter(status='active').order_by('name')

    return render(request, 'planning/planning_detail.html', {
        'planning': planning,
        'collaborators': collaborators,
        'subcontractors': subcontractors,
        'period_choices': PlanningWorker.PERIOD_CHOICES,
    })


@login_required
def planning_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        date = request.POST.get('date')
        notes = request.POST.get('notes', '')
        planning, _ = Planning.objects.get_or_create(
            project=project, date=date, defaults={'notes': notes}
        )
        return redirect('planning:detail', pk=planning.pk)
    return render(request, 'planning/planning_form.html', {'project': project})


@login_required
@require_POST
def planning_delete(request, pk):
    planning = get_object_or_404(Planning, pk=pk)
    planning.delete()
    return redirect('planning:list')


@login_required
@require_POST
def planning_add_worker(request, planning_pk):
    planning = get_object_or_404(Planning, pk=planning_pk)
    data = json.loads(request.body)
    worker = get_object_or_404(Collaborator, pk=data.get('worker_id'))
    pw, created = PlanningWorker.objects.get_or_create(
        planning=planning, worker=worker,
        defaults={
            'subcontractor_id': data.get('subcontractor_id') or None,
            'period': data.get('period', 'full_day'),
            'start_time': data.get('start_time') or None,
            'end_time': data.get('end_time') or None,
            'role': data.get('role', ''),
            'notes': data.get('notes', ''),
            'is_present': True,
        }
    )
    if not created:
        return JsonResponse({'error': 'Worker already added.'}, status=400)
    return JsonResponse({
        'id': pw.pk, 'worker_name': worker.name,
        'period': pw.get_period_display(), 'period_key': pw.period,
        'role': pw.role, 'is_present': pw.is_present,
        'subcontractor': pw.subcontractor.name if pw.subcontractor else None,
    })


@login_required
@require_POST
def planning_update_worker(request, pw_pk):
    pw = get_object_or_404(PlanningWorker, pk=pw_pk)
    data = json.loads(request.body)
    for field in ['is_present', 'period', 'role', 'notes']:
        if field in data:
            setattr(pw, field, data[field])
    if 'start_time' in data:
        pw.start_time = data['start_time'] or None
    if 'end_time' in data:
        pw.end_time = data['end_time'] or None
    pw.save()
    return JsonResponse({'id': pw.pk, 'is_present': pw.is_present,
                         'period': pw.get_period_display(), 'period_key': pw.period})


@login_required
@require_POST
def planning_remove_worker(request, pw_pk):
    get_object_or_404(PlanningWorker, pk=pw_pk).delete()
    return JsonResponse({'ok': True})


@login_required
@require_POST
def planning_add_subcontractor(request, planning_pk):
    planning = get_object_or_404(Planning, pk=planning_pk)
    data = json.loads(request.body)
    sub = get_object_or_404(Subcontractor, pk=data.get('subcontractor_id'))
    ps, created = PlanningSubcontractor.objects.get_or_create(
        planning=planning, subcontractor=sub,
        defaults={'notes': data.get('notes', '')}
    )
    if not created:
        return JsonResponse({'error': 'Already added.'}, status=400)
    return JsonResponse({'id': ps.pk, 'subcontractor_name': sub.name, 'notes': ps.notes})


@login_required
@require_POST
def planning_remove_subcontractor(request, ps_pk):
    get_object_or_404(PlanningSubcontractor, pk=ps_pk).delete()
    return JsonResponse({'ok': True})