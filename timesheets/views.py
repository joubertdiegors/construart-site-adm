from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, Q
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import json

from .models import Timesheet
from projects.models import Project
from workforce.models import Collaborator
from planning.models import Planning, PlanningWorker


# ─────────────────────────────────────────────────────────────
# 📋 LISTA / DASHBOARD  (filtros: projeto, trabalhador, período)
# ─────────────────────────────────────────────────────────────
@login_required
def timesheet_list(request):
    projects    = Project.objects.filter(status__in=['planning', 'active']).order_by('name')
    workers     = Collaborator.objects.filter(status='active').select_related('company').order_by('name')

    # Filtros
    project_id  = request.GET.get('project')
    worker_id   = request.GET.get('worker')
    date_from   = request.GET.get('date_from')
    date_to     = request.GET.get('date_to')

    qs = Timesheet.objects.select_related(
        'worker', 'worker__company', 'project', 'planning_worker'
    ).order_by('-date', 'worker__name')

    if project_id:
        qs = qs.filter(project_id=project_id)
    if worker_id:
        qs = qs.filter(worker_id=worker_id)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    # Totais para o painel de resumo
    timesheets = list(qs)
    total_hours = sum(t.computed_hours for t in timesheets)
    total_cost  = sum(t.total_cost for t in timesheets)

    selected_project = None
    if project_id:
        selected_project = Project.objects.filter(pk=project_id).first()

    return render(request, 'timesheets/timesheet_list.html', {
        'timesheets':        timesheets,
        'projects':          projects,
        'workers':           workers,
        'total_hours':       total_hours,
        'total_cost':        total_cost,
        'selected_project':  selected_project,
        'filters': {
            'project':   project_id or '',
            'worker':    worker_id  or '',
            'date_from': date_from  or '',
            'date_to':   date_to   or '',
        },
    })


# ─────────────────────────────────────────────────────────────
# ➕ CRIAR (manual ou pré-preenchido a partir do planning)
# ─────────────────────────────────────────────────────────────
@login_required
def timesheet_create(request):
    projects = Project.objects.filter(status__in=['planning', 'active']).order_by('name')
    workers  = Collaborator.objects.filter(status='active').select_related('company').order_by('name')

    # Pré-preencher a partir de um PlanningWorker
    pw_pk = request.GET.get('planning_worker')
    prefill = {}
    planning_worker = None
    if pw_pk:
        planning_worker = PlanningWorker.objects.select_related(
            'planning__project', 'worker'
        ).filter(pk=pw_pk).first()
        if planning_worker:
            prefill = {
                'worker_id':   planning_worker.worker_id,
                'project_id':  planning_worker.planning.project_id,
                'date':        planning_worker.planning.date.isoformat(),
                'start_time':  planning_worker.start_time.strftime('%H:%M') if planning_worker.start_time else '',
                'end_time':    planning_worker.end_time.strftime('%H:%M')   if planning_worker.end_time   else '',
            }

    if request.method == 'POST':
        worker_id         = request.POST.get('worker')
        project_id        = request.POST.get('project')
        date              = request.POST.get('date')
        start_time        = request.POST.get('start_time') or None
        end_time          = request.POST.get('end_time')   or None
        hours             = request.POST.get('hours')      or None
        is_overtime       = request.POST.get('is_overtime') == 'on'
        overtime_rate     = request.POST.get('overtime_rate') or '1.50'
        notes             = request.POST.get('notes', '')
        pw_id             = request.POST.get('planning_worker_id') or None

        errors = {}
        if not worker_id:  errors['worker']  = "Campo obrigatório."
        if not project_id: errors['project'] = "Campo obrigatório."
        if not date:       errors['date']    = "Campo obrigatório."
        if not start_time and not hours:
            errors['hours'] = "Indique horas de início/fim ou total de horas."

        if not errors:
            ts = Timesheet(
                worker_id=worker_id,
                project_id=project_id,
                date=date,
                start_time=start_time or None,
                end_time=end_time or None,
                hours=Decimal(hours) if hours else None,
                is_overtime=is_overtime,
                overtime_rate=Decimal(overtime_rate),
                notes=notes,
                planning_worker_id=pw_id or None,
            )
            try:
                ts.full_clean()
                ts.save()
                next_url = request.POST.get('next') or 'timesheets:list'
                return redirect(next_url)
            except Exception as e:
                errors['__all__'] = str(e)

        return render(request, 'timesheets/timesheet_form.html', {
            'projects': projects, 'workers': workers,
            'errors': errors, 'post': request.POST,
            'planning_worker': planning_worker,
        })

    return render(request, 'timesheets/timesheet_form.html', {
        'projects': projects, 'workers': workers,
        'prefill': prefill, 'planning_worker': planning_worker,
    })


# ─────────────────────────────────────────────────────────────
# ✏️ EDITAR
# ─────────────────────────────────────────────────────────────
@login_required
def timesheet_update(request, pk):
    ts       = get_object_or_404(Timesheet, pk=pk)
    projects = Project.objects.filter(status__in=['planning', 'active']).order_by('name')
    workers  = Collaborator.objects.filter(status='active').select_related('company').order_by('name')

    if request.method == 'POST':
        ts.worker_id      = request.POST.get('worker')
        ts.project_id     = request.POST.get('project')
        ts.date           = request.POST.get('date')
        ts.start_time     = request.POST.get('start_time') or None
        ts.end_time       = request.POST.get('end_time')   or None
        h = request.POST.get('hours')
        ts.hours          = Decimal(h) if h else None
        ts.is_overtime    = request.POST.get('is_overtime') == 'on'
        ts.overtime_rate  = Decimal(request.POST.get('overtime_rate') or '1.50')
        ts.notes          = request.POST.get('notes', '')

        errors = {}
        if not ts.start_time and not ts.hours:
            errors['hours'] = "Indique horas de início/fim ou total de horas."

        if not errors:
            try:
                ts.full_clean()
                ts.save()
                return redirect('timesheets:list')
            except Exception as e:
                errors['__all__'] = str(e)

        return render(request, 'timesheets/timesheet_form.html', {
            'projects': projects, 'workers': workers,
            'errors': errors, 'ts': ts, 'editing': True,
        })

    return render(request, 'timesheets/timesheet_form.html', {
        'projects': projects, 'workers': workers,
        'ts': ts, 'editing': True,
    })


# ─────────────────────────────────────────────────────────────
# 🗑️ APAGAR
# ─────────────────────────────────────────────────────────────
@login_required
@require_POST
def timesheet_delete(request, pk):
    get_object_or_404(Timesheet, pk=pk).delete()
    return redirect('timesheets:list')


# ─────────────────────────────────────────────────────────────
# 📊 RESUMO POR PROJETO  (dados para relatório / futura fatura)
# ─────────────────────────────────────────────────────────────
@login_required
def timesheet_project_summary(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    timesheets = Timesheet.objects.filter(project=project).select_related(
        'worker', 'worker__company'
    ).order_by('-date', 'worker__name')

    # Agrupar por trabalhador
    from collections import defaultdict
    by_worker = defaultdict(lambda: {'entries': [], 'total_hours': Decimal('0'), 'total_cost': Decimal('0')})
    for ts in timesheets:
        w = by_worker[ts.worker]
        w['worker'] = ts.worker
        w['entries'].append(ts)
        w['total_hours'] += ts.computed_hours
        w['total_cost']  += ts.total_cost

    summary = sorted(by_worker.values(), key=lambda x: x['worker'].name)
    grand_hours = sum(w['total_hours'] for w in summary)
    grand_cost  = sum(w['total_cost']  for w in summary)

    return render(request, 'timesheets/timesheet_summary.html', {
        'project':     project,
        'summary':     summary,
        'grand_hours': grand_hours,
        'grand_cost':  grand_cost,
        'timesheets':  timesheets,
    })


# ─────────────────────────────────────────────────────────────
# ⚡ API — preencher timesheets em bulk a partir do planning do dia
# ─────────────────────────────────────────────────────────────
@login_required
@require_POST
def timesheet_bulk_from_planning(request, planning_pk):
    """
    Cria automaticamente um Timesheet para cada PlanningWorker presente
    no dia, usando os horários do planning como base.
    Ignora os que já têm timesheet.
    """
    planning = get_object_or_404(Planning, pk=planning_pk)
    data     = json.loads(request.body)
    created  = []
    skipped  = []

    for pw in planning.planning_workers.filter(is_present=True).select_related('worker'):
        # Já existe?
        exists = Timesheet.objects.filter(
            worker=pw.worker, project=planning.project, date=planning.date
        ).exists()
        if exists:
            skipped.append(pw.worker.name)
            continue

        ts = Timesheet(
            worker=pw.worker,
            project=planning.project,
            date=planning.date,
            start_time=pw.start_time,
            end_time=pw.end_time,
            hours=data.get('default_hours') or (None if pw.start_time else Decimal('8')),
            planning_worker=pw,
            notes=f"Auto-criado a partir do planning de {planning.date}",
        )
        ts.save()
        created.append(pw.worker.name)

    return JsonResponse({
        'created': created,
        'skipped': skipped,
        'count':   len(created),
    })