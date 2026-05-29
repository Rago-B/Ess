from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from .models import Task
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Task  # Ensures your local Task model is imported safely

User = get_user_model()

@login_required
def my_tasks_view(request):
    """
    📋 ROLE-BASED TASK WORKSPACE ENGINE:
    HR / Admin: Can monitor all corporate tasks, view all team lines, and assign tasks to anyone.
    Employees: Can only view, update, and self-assign tasks linked strictly to themselves.
    """
    user = request.user
    user_email_clean = user.email.strip() if user.email else ""
    active_filter = request.GET.get('filter', 'All')
    
    print(f"\n[TASK ACCESS] User: {user.email} | Role: '{getattr(user, 'role', 'employee')}' | Filter: {active_filter}\n")

    # =========================================================================
    # 📥 1. DATA VISIBILITY SPLIT (GET TRAFFIC CHECK)
    # =========================================================================
    if user.role in ['admin', 'hr']:
        # HR and Admins pull tasks globally across the whole platform
        base_queryset = Task.objects.all().select_related('assigned_to', 'created_by')
        team_members = User.objects.filter(is_active=True)
    else:
        # 🔒 SECURITY BOUNDARY: Employees are strictly locked to their own assignments!
        query_condition = Q(assigned_to=user)
        if user_email_clean:
            query_condition |= Q(assigned_to_email__iexact=user_email_clean)
        
        base_queryset = Task.objects.filter(query_condition).select_related('assigned_to', 'created_by')
        team_members = User.objects.filter(id=user.id)

    # Apply completion filters (Pending vs Completed states checks)
    if active_filter.lower() == 'pending':
        tasks_queryset = base_queryset.exclude(status='Completed')
    elif active_filter.lower() == 'completed':
        tasks_queryset = base_queryset.filter(status='Completed')
    elif active_filter.lower() == 'in progress':
        tasks_queryset = base_queryset.filter(status='In Progress')
    else:
        tasks_queryset = base_queryset

    # Order tasks by due date and creation log history timestamps chronologically
    tasks_list = tasks_queryset.order_by('due_date', '-created_at')

    # Enhanced loops array to inject dynamic visual overdue layout warning tags
    today_date = timezone.now().date()
    enhanced_tasks = []
    for task in tasks_list:
        is_overdue = task.due_date < today_date and task.status != 'Completed' if task.due_date else False
        
        # Native Python string extraction handles avatar initials smoothly
        user_initial = "U"
        if task.assigned_to and task.assigned_to.username:
            user_initial = task.assigned_to.username.upper()[0]

        enhanced_tasks.append({
            'data': task,
            'is_overdue': is_overdue,
            'initial': user_initial  # Passed cleanly into your mytasks.html table loop
        })

    # =========================================================================
    # 📤 2. DATA TRANSACTION LAYER (POST TRAFFIC CHECK)
    # =========================================================================
    if request.method == "POST":
        
        # 🎯 TRACK A: DYNAMIC MUTATION TRIGGER INTERACTION (Mark In Progress / Completed)
        if "update_task_status_id" in request.POST:
            task_id = request.POST.get("update_task_status_id")
            target_state = request.POST.get("target_status_value", "Completed")
            
            task_obj = get_object_or_404(Task, id=task_id)
            
            # 🔒 SECURITY CONSTRAINT: Block standard users from editing other people's rows
            if user.role not in ['admin', 'hr'] and task_obj.assigned_to != user:
                messages.error(request, "Unauthorized status transaction request rejected.")
            else:
                task_obj.status = target_state
                task_obj.save()
                messages.success(request, f"Task '{task_obj.title}' successfully updated to {target_state}!")
            return redirect(request.path_info)

        # 🎯 TRACK B: CREATE TASK FROM MODAL SUBMISSION
        if "create_task" in request.POST:
            title = request.POST.get("title")
            description = request.POST.get("description")
            priority = request.POST.get("priority", "Medium")
            due_date = request.POST.get("due_date")
            notes = request.POST.get("notes")

            # Determine target assignment based on role capability rules parameters
            if user.role in ['admin', 'hr']:
                target_emp_id = request.POST.get("assigned_to_user_id") or request.POST.get("employee_id")
                assignee_obj = get_object_or_404(User, id=target_emp_id) if target_emp_id else user
            else:
                assignee_obj = user

            try:
                Task.objects.create(
                    title=title,
                    description=description,
                    assigned_to=assignee_obj,
                    assigned_to_email=assignee_obj.email,
                    priority=priority,
                    due_date=due_date if due_date else None,
                    notes=notes,
                    created_by=user,
                    status='Pending'
                )
                messages.success(request, f'Task successfully created and assigned to {assignee_obj.username}!')
            except Exception as e:
                messages.error(request, f'Failed to commit task parameters: {e}')
                
            return redirect(request.path_info)

    context = {
        'tasks': enhanced_tasks,
        'employees': team_members, 
        'current_filter': active_filter,
        'current_role': user.role, 
        'active_section': 'my_tasks'
    }
    return render(request, "task_management/mytasks.html", context)






@login_required
def update_task_status_view(request, task_id):
    """
    MATCHES Mongoose: router.put('/my-tasks/:id')
    Secures data entry mutations by verifying the worker holds matching identity constraints.
    """
    if request.method == "POST":
        new_status = request.POST.get("status")
        
        # Matches Mongoose: Task.findOne({ _id: req.params.id, assignedTo: req.session.userId })
        # This securely guarantees an operator cannot manipulate someone else's workflow rows
        task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
        
        if new_status in ['Pending', 'In Progress', 'Completed']:
            task.status = new_status
            
            # Automatically stamp completion timestamps if the state progresses to Completed
            if new_status == 'Completed':
                task.completed_at = timezone.now()
            else:
                task.completed_at = None
                
            task.save()
            messages.success(request, f"Task marked as {new_status} smoothly.")
        else:
            messages.error(request, "Invalid workflow status update parameter rejected.")
            
    return redirect(f"/tasks/my-tasks/?filter={request.GET.get('current_filter', 'All')}")


# Add this separate view function inside apps/task_manager/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Task

@login_required
def task_board_view(request):
    """
    MATCHES React Component: TaskBoard
    Fetches all tasks to populate the global multi-column board view.
    """
    today_date = timezone.now().date()
    
    # Fetch all tasks across the company (or filter by user projects if needed)
    all_tasks = Task.objects.all().select_related('assigned_to').order_by('due_date', '-created_at')
    
    # Calculate global totals for top statistic overview cards
    total_count = all_tasks.count()
    pending_count = all_tasks.filter(status='Pending').count()
    progress_count = all_tasks.filter(status='In Progress').count()
    completed_count = all_tasks.filter(status='Completed').count()

    # Split the tasks into separate arrays for our template columns loop mapping
    pending_tasks = []
    progress_tasks = []
    completed_tasks = []

    for task in all_tasks:
        is_overdue = task.due_date < today_date and task.status != 'Completed' if task.due_date else False
        task_payload = {'data': task, 'is_overdue': is_overdue}
        
        if task.status == 'Pending':
            pending_tasks.append(task_payload)
        elif task.status == 'In Progress':
            progress_tasks.append(task_payload)
        elif task.status == 'Completed':
            completed_tasks.append(task_payload)

    context = {
        'pending_tasks': pending_tasks,
        'progress_tasks': progress_tasks,
        'completed_tasks': completed_tasks,
        'total_count': total_count,
        'pending_count': pending_count,
        'progress_count': progress_count,
        'completed_count': completed_count,
        'active_section': 'task_board' # Anchors active sidebar highlighting layout
    }
    return render(request, "task_management/kanbanboard.html", context)


# Inside apps/task_management/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

def assign_task_view(request):
    """
    Handles creating and delegating tasks to specific employees.
    """
    employees = User.objects.filter(is_active=True)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        assigned_to_id = request.POST.get("employee_id")
        priority = request.POST.get("priority", "Medium")
        due_date = request.POST.get("due_date")
        notes = request.POST.get("notes")

        try:
            target_employee = User.objects.get(id=assigned_to_id)
            
            Task.objects.create(
                title=title,
                description=description,
                assigned_to=target_employee,
                assigned_to_email=target_employee.email,
                priority=priority,
                due_date=due_date if due_date else None,
                notes=notes,
                created_by=request.user,
                status='Pending'
            )
            messages.success(request, 'Task assigned and delegated successfully!')
            return redirect('task_list') # Redirects back to global task list overview
        except Exception as e:
            messages.error(request, f'Failed to assign task: {e}')

    return render(request, "task_management/assigntask.html", {'employees': employees})

# Inside apps/task_management/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


# Open apps/task_management/views.py

@login_required
def add_task_creation_view(request):
    system_employees = User.objects.filter(is_active=True).order_by('full_name', 'username')

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        
        # FIX: Safety fallback check to capture whichever key format is used by your HTML select field
        assigned_to_id = request.POST.get("assigned_to") or request.POST.get("assigned_to_id") or request.POST.get("employee_id")
        
        priority = request.POST.get("priority", "Medium")
        due_date = request.POST.get("due_date")
        notes = request.POST.get("notes", "").strip()

        clean_due_date = due_date if due_date else None

        try:
            assigned_user_obj = None
            assigned_email = None
            
            if assigned_to_id and assigned_to_id.strip() != "":
                assigned_user_obj = User.objects.get(id=assigned_to_id)
                assigned_email = assigned_user_obj.email

            # Save cleanly directly into your separate model table rows
            Task.objects.create(
                title=title,
                description=description if description else None,
                assigned_to=assigned_user_obj,
                assigned_to_email=assigned_email,
                priority=priority,
                due_date=clean_due_date,
                notes=notes if notes else None,
                created_by=request.user,
                status='Pending'
            )
            messages.success(request, 'Task created and delegated successfully!')
            return redirect('task_board')
            
        except Exception as e:
            messages.error(request, f'Failed to process task delegation: {e}')

    context = {
        'employees': system_employees,
        'active_section': 'task_board'
    }
    return render(request, "task_management/addtask.html", context)
