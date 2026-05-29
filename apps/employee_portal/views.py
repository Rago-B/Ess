from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q

@login_required
def employee_dashboard(request):
    from apps.task_management.models import Task
    from apps.visitor_management.models import Visitor

    user = request.user
    today = timezone.now().date()

    # --- Task stats for the logged-in user ---
    user_email = (user.email or "").strip()
    q = Q(assigned_to=user)
    if user_email:
        q |= Q(assigned_to_email__iexact=user_email)

    if getattr(user, 'role', 'employee') in ['admin', 'hr']:
        user_tasks = Task.objects.all().select_related('assigned_to')
    else:
        user_tasks = Task.objects.filter(q).select_related('assigned_to')

    total_tasks     = user_tasks.count()
    pending_tasks   = user_tasks.filter(status='Pending').count()
    inprogress_tasks = user_tasks.filter(status='In Progress').count()
    completed_tasks = user_tasks.filter(status='Completed').count()
    overdue_tasks   = user_tasks.filter(due_date__lt=today).exclude(status='Completed').count()

    # Recent tasks (latest 5)
    recent_tasks = []
    for task in user_tasks.order_by('-created_at')[:5]:
        is_overdue = task.due_date and task.due_date < today and task.status != 'Completed'
        recent_tasks.append({'data': task, 'is_overdue': is_overdue})

    # --- Visitor stats (today) ---
    total_visitors_today = Visitor.objects.filter(check_in__date=today).count()
    checked_in_now       = Visitor.objects.filter(check_in__date=today, check_out__isnull=True).count()
    checked_out_today    = Visitor.objects.filter(check_in__date=today, check_out__isnull=False).count()
    recent_visitors      = Visitor.objects.filter(check_in__date=today).order_by('-check_in')[:4]

    context = {
        'active_section': 'dashboard',
        'today': today,
        # task stats
        'total_tasks':      total_tasks,
        'pending_tasks':    pending_tasks,
        'inprogress_tasks': inprogress_tasks,
        'completed_tasks':  completed_tasks,
        'overdue_tasks':    overdue_tasks,
        'recent_tasks':     recent_tasks,
        # visitor stats
        'total_visitors_today': total_visitors_today,
        'checked_in_now':       checked_in_now,
        'checked_out_today':    checked_out_today,
        'recent_visitors':      recent_visitors,
    }
    return render(request, 'employee_portal/dashboard.html', context)
