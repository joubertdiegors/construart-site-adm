from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.utils import timezone
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
    import calendar as _cal
    qs = Timesheet.objects.select_related(
        'worker', 'worker__company', 'project', 'project__client'
    ).order_by('-date', 'worker__name')

    timesheets  = list(qs)
    total_hours = sum(t.computed_hours for t in timesheets)

    # Opções de filtro client-side
    seen_obra = {}; seen_worker = {}; seen_client = {}; seen_sub = {}
    all_dates = set()
    for t in timesheets:
        all_dates.add(t.date.isoformat())

        pid = t.project_id
        if pid not in seen_obra:
            seen_obra[pid] = {'id': pid, 'name': t.project.name, 'count': 0}
        seen_obra[pid]['count'] += 1

        wid = t.worker_id
        if wid not in seen_worker:
            seen_worker[wid] = {'id': wid, 'name': t.worker.name, 'count': 0}
        seen_worker[wid]['count'] += 1

        if t.project.client_id:
            cid = t.project.client_id
            if cid not in seen_client:
                seen_client[cid] = {'id': cid, 'name': t.project.client.name, 'count': 0}
            seen_client[cid]['count'] += 1

        sid = t.worker.company_id
        if sid not in seen_sub:
            seen_sub[sid] = {'id': sid, 'name': t.worker.company.name, 'count': 0}
        seen_sub[sid]['count'] += 1

    today = timezone.localdate()
    response = render(request, 'timesheets/timesheet_list.html', {
        'timesheets':     timesheets,
        'total_hours':    total_hours,
        'filter_obras':   sorted(seen_obra.values(),   key=lambda x: x['name']),
        'filter_workers': sorted(seen_worker.values(),  key=lambda x: x['name']),
        'filter_clients': sorted(seen_client.values(),  key=lambda x: x['name']),
        'filter_subs':    sorted(seen_sub.values(),    key=lambda x: x['name']),
        'all_dates_json': list(sorted(all_dates)),
        'today_str':      today.isoformat(),
        'cal_year':       today.year,
        'cal_month':      today.month,
    })
    response['Cache-Control'] = 'no-store'
    return response


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


# ─────────────────────────────────────────────────────────────
# 📅 BOARD DIÁRIO — lista editável gerada a partir do planning
# ─────────────────────────────────────────────────────────────
def _can_edit_timesheets(user):
    return user.is_staff or user.is_superuser or user.has_perm('timesheets.change_timesheet')


@login_required
def timesheet_daily_board(request):
    if not _can_edit_timesheets(request.user):
        raise PermissionDenied
    raw = (request.GET.get('date') or '').strip()[:10]
    if raw:
        try:
            selected_date = datetime.strptime(raw, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.localdate()
    else:
        selected_date = timezone.localdate()

    # Garante que a URL sempre tem ?date= explícito (evita perda de contexto ao navegar)
    if not raw:
        from django.shortcuts import redirect as _redirect
        return _redirect(f"{request.path}?date={selected_date.isoformat()}")

    # Todas as linhas do planning deste dia
    planning_rows = (
        PlanningWorker.objects
        .filter(planning__date=selected_date)
        .select_related('worker__company', 'planning__project__client')
        .order_by('worker__name', 'planning__project__name')
    )

    # Timesheets já existentes para este dia, indexados por (worker_id, project_id)
    existing = {
        (ts.worker_id, ts.project_id): ts
        for ts in Timesheet.objects.filter(date=selected_date)
    }

    rows = []
    for pw in planning_rows:
        key = (pw.worker_id, pw.planning.project_id)
        ts  = existing.get(key)
        rows.append({
            'pw':          pw,
            'worker':      pw.worker,
            'project':     pw.planning.project,
            'timesheet':   ts,
            'hours':       ts.hours if ts else None,
            'notes':       ts.notes if ts else '',
            'ts_id':       ts.pk   if ts else None,
        })

    # Dias do mês com planning (para calendário)
    import calendar as _cal
    month_start = selected_date.replace(day=1)
    last_day    = _cal.monthrange(selected_date.year, selected_date.month)[1]
    month_end   = selected_date.replace(day=last_day)
    active_days = set(
        Planning.objects.filter(date__gte=month_start, date__lte=month_end)
        .values_list('date__day', flat=True).distinct()
    )

    # Opções de filtro (deduplicated, ordenadas)
    seen_obra = {}; seen_worker = {}; seen_client = {}; seen_sub = {}
    for r in rows:
        pid = r['project'].pk
        if pid not in seen_obra:
            seen_obra[pid] = {'id': pid, 'name': r['project'].name, 'count': 0}
        seen_obra[pid]['count'] += 1

        wid = r['worker'].pk
        if wid not in seen_worker:
            seen_worker[wid] = {'id': wid, 'name': r['worker'].name, 'count': 0}
        seen_worker[wid]['count'] += 1

        if r['project'].client_id:
            cid = r['project'].client_id
            if cid not in seen_client:
                seen_client[cid] = {'id': cid, 'name': r['project'].client.name, 'count': 0}
            seen_client[cid]['count'] += 1

        sid = r['worker'].company_id
        if sid not in seen_sub:
            seen_sub[sid] = {'id': sid, 'name': r['worker'].company.name, 'count': 0}
        seen_sub[sid]['count'] += 1

    response = render(request, 'timesheets/timesheet_daily_board.html', {
        'selected_date':  selected_date,
        'date_str':       selected_date.isoformat(),
        'today_str':      timezone.localdate().isoformat(),
        'rows':           rows,
        'active_days':    list(active_days),
        'cal_year':       selected_date.year,
        'cal_month':      selected_date.month,
        'filter_obras':   sorted(seen_obra.values(),  key=lambda x: x['name']),
        'filter_workers': sorted(seen_worker.values(), key=lambda x: x['name']),
        'filter_clients': sorted(seen_client.values(), key=lambda x: x['name']),
        'filter_subs':    sorted(seen_sub.values(),   key=lambda x: x['name']),
    })
    response['Cache-Control'] = 'no-store'
    return response


@login_required
def timesheet_calendar_days(request):
    """Retorna os dias do mês que têm planning, para o calendário JS."""
    import calendar as _cal
    try:
        year  = int(request.GET.get('year',  timezone.localdate().year))
        month = int(request.GET.get('month', timezone.localdate().month))
    except (ValueError, TypeError):
        return JsonResponse({'active_days': []})
    last_day    = _cal.monthrange(year, month)[1]
    month_start = datetime(year, month, 1).date()
    month_end   = datetime(year, month, last_day).date()
    days = list(
        Planning.objects.filter(date__gte=month_start, date__lte=month_end)
        .values_list('date__day', flat=True).distinct()
    )
    return JsonResponse({'active_days': days})


@login_required
@require_POST
def timesheet_daily_board_save(request):
    """Salva em bulk as linhas do board diário."""
    if not _can_edit_timesheets(request.user):
        raise PermissionDenied
    try:
        data = json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido.'}, status=400)

    date_str = (data.get('date') or '')[:10]
    try:
        day = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Data inválida.'}, status=400)

    lines = data.get('lines', [])
    if len(lines) != 1:
        return JsonResponse({'error': 'Envie uma linha de cada vez.'}, status=400)

    line = lines[0]
    hours_raw = (line.get('hours') or '').strip()
    if not hours_raw:
        return JsonResponse({'ok': True, 'saved': 0, 'skipped': 1})

    try:
        hours_val = Decimal(hours_raw.replace(',', '.'))
    except Exception:
        return JsonResponse({'error': 'Valor de horas inválido.'}, status=400)

    try:
        worker_id  = int(line['worker_id'])
        project_id = int(line['project_id'])
    except (KeyError, TypeError, ValueError):
        return JsonResponse({'error': 'worker_id / project_id inválidos.'}, status=400)

    pw_id = line.get('pw_id')
    notes = (line.get('notes') or '').strip()

    try:
        Timesheet.objects.update_or_create(
            worker_id=worker_id,
            project_id=project_id,
            date=day,
            defaults={
                'hours':              hours_val,
                'notes':              notes,
                'planning_worker_id': int(pw_id) if pw_id else None,
            },
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'ok': True, 'saved': 1, 'skipped': 0})