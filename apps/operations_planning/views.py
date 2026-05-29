from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Bench
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

def bench_management_view(request):
    """
    MATCHES Mongoose: router.get('/') and router.post('/')
    """
    # 1. Fetch entries with populate mappings -> Bench.find().populate('emp_id').sort({ createdAt: -1 })
    bench_entries = Bench.objects.all().select_related('employee').order_by('-created_at')
    
    # Preload all active employees to populate the check-in modal select box
    all_employees = User.objects.filter(is_active=True)

    # Replicate Mongoose .map() enhanced logic to compute metadata on the fly
    enhanced_rows = []
    current_year = timezone.now().year
    
    for entry in bench_entries:
        emp = entry.employee
        
        # Calculate experience: Math.floor((new Date() - new Date(emp.doj)) / (365 * 24 * ...))
        # Safely fallbacks to 0 if your Employee model doesn't have a 'doj' field or if it is null
        if emp and hasattr(emp, 'doj') and emp.doj:
            # Simple, accurate calculation for years of experience
            experience_years = current_year - emp.doj.year - ((timezone.now().date() < date(current_year, emp.doj.month, emp.doj.day)))
            experience_str = f"{max(0, experience_years)} Yrs"
        else:
            experience_str = "0 Yrs"

        # Parse comma skills text value into clean Python iterables -> entry.skills.split(',').map(s => s.trim())
        parsed_skills = [s.strip() for s in entry.skills.split(',')] if entry.skills else []

        enhanced_rows.append({
            'record': entry,
            'bench_id': entry.id,
            'emp_id': emp.id if emp else None,
            'emp_name': f"{emp.first_name} {emp.last_name or ''}".strip() if emp else "Unknown",
            'email': emp.email if emp else "",
            'designation': getattr(emp, 'designation', 'Employee'),
            'bench_start': entry.created_at,
            'experience': experience_str,
            'skills': parsed_skills
        })

    # 2. MATCHES Mongoose: router.post('/') -> Adds an employee to the bench
    if request.method == "POST":
        emp_id = request.POST.get('employee_id')
        skills_input = request.POST.get('skills', '').strip()

        # Replicates Mongoose: const existing = await Bench.findOne({ emp_id });
        already_on_bench = Bench.objects.filter(employee_id=emp_id).exists()
        
        if already_on_bench:
            messages.error(request, 'Employee is already on bench!')
        else:
            try:
                employee_obj = User.objects.get(id=emp_id)
                Bench.objects.create(
                    employee=employee_obj,
                    skills=skills_input
                )
                messages.success(request, 'Employee added to bench cleanly!')
            except Exception as e:
                messages.error(request, f'Failed to assign to bench: {e}')
                
        return redirect('bench_strength')

    context = {
        'bench_list': enhanced_rows,
        'employees': all_employees,
        'active_section': 'bench_strength'
    }
    return render(request, "operations_planning/benchstrength.html", context)


def remove_from_bench_view(request, record_id):
    """
    MATCHES Mongoose: router.delete('/:id') -> router.delete('/:id')
    Removes employee from bench (allocates them to a project)
    """
    bench_record = get_object_or_404(Bench, id=record_id)
    bench_record.delete()
    messages.success(request, 'Employee removed from bench and marked as allocated!')
    return redirect('bench_strength')

from .models import Travel
# Open apps/operations_planning/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def travel_management_view(request):
    """
    ✈️ ROLE-BASED TRAVEL MANAGEMENT ENGINE:
    HR / Admin: Can view, create, edit, and update ALL company travel requests.
    Employees: Can ONLY view and submit their own personal travel request entries.
    """
    current_user = request.user
    
    # =========================================================================
    # 📥 1. DATA VISIBILITY SPLIT (GET TRAFFIC CHECK)
    # =========================================================================
    if current_user.role in ['admin', 'hr']:
        # HR/Admin see everything across the entire organization
        travel_list = Travel.objects.all().select_related('employee').order_by('-created_at')
        employees_pool = User.objects.filter(is_active=True)
    else:
        # 🔒 SECURITY BOUNDARY: Employees are locked to their own database row entries only!
        travel_list = Travel.objects.filter(employee=current_user).order_by('-created_at')
        # Employees can only create requests for themselves, so the dropdown pool is restricted
        employees_pool = User.objects.filter(id=current_user.id)

    # =========================================================================
    # 📤 2. DATA TRANSACTION LAYER (POST TRAFFIC CHECK)
    # =========================================================================
    if request.method == "POST":
        selected_id = request.POST.get("selected_id")
        
        # Extract variables from form fields
        travel_type = request.POST.get("travel_type", "Domestic")
        from_loc = request.POST.get("from_location") or request.POST.get("fromLocation")
        to_loc = request.POST.get("to_location") or request.POST.get("toLocation")
        purpose = request.POST.get("purpose")
        departure = request.POST.get("departure_date") or request.POST.get("departureDate")
        returning = request.POST.get("return_date") or request.POST.get("returnDate")
        
        # Enforce corporate authorization rules for Status modifications
        if current_user.role in ['admin', 'hr']:
            form_status = request.POST.get("status", "Pending")
            # Admins can assign requests to any active employee via the form input selection
            emp_id = request.POST.get("employee_id") or request.POST.get("employee")
        else:
            # 🔒 SECURITY BOUNDARY: Employees are locked to 'Pending' status and cannot fake other User IDs
            form_status = "Pending"
            emp_id = current_user.id

        clean_departure = departure if departure else None
        clean_return = returning if returning else None

        try:
            employee_obj = User.objects.get(id=emp_id)

            if selected_id:  # Edit / Update path logic block
                # Fetch target instance safely
                travel = get_object_or_404(Travel, id=selected_id)
                
                # 🔒 SECURITY BOUNDARY: Verify an employee isn't intercepting someone else's record ID
                if current_user.role not in ['admin', 'hr'] and travel.employee != current_user:
                    messages.error(request, "Access denied. Altering external corporate records is restricted.")
                    return redirect('travel_management')
                
                travel.employee = employee_obj
                travel.travel_type = travel_type
                travel.from_location = from_loc
                travel.to_location = to_loc
                travel.purpose = purpose
                travel.departure_date = clean_departure
                travel.return_date = clean_return
                travel.status = form_status
                travel.save()
                messages.success(request, 'Travel request updated successfully!')
                
            else:  # Create brand new database request line item row
                Travel.objects.create(
                    employee=employee_obj,
                    travel_type=travel_type,
                    from_location=from_loc,
                    to_location=to_loc,
                    purpose=purpose,
                    departure_date=clean_departure,
                    return_date=clean_return,
                    status=form_status
                )
                messages.success(request, 'Travel request created successfully!')
                
        except Exception as e:
            messages.error(request, f"Submission tracking block failed: {e}")

        return redirect('travel_management')

    context = {
        'travels': travel_list,
        'employees': employees_pool,
        'current_role': current_user.role, # Passed to adjust frontend visibility components
        'active_section': 'travel_requests'
    }
    return render(request, "operations_planning/travelmanagement.html", context)



def delete_travel_view(request, travel_id):
    travel = get_object_or_404(Travel, id=travel_id)
    travel.delete()
    messages.success(request, 'Travel record deleted successfully!')
    return redirect('travel_requests')


from django.shortcuts import render
from .models import CostMonitoring

def cost_monitoring_view(request):
    """
    Matches Mongoose/React: axios.get('/api/v2/admin-ext/costs')
    Calculates reactive summary card metrics.
    """
    # Fetch all project finance tracker entries
    costs_list = CostMonitoring.objects.all().order_by('-created_at')

    # Replicate React .reduce() calculations using Python sum comprehension filters
    total_budgeted = sum(item.budget for item in costs_list)
    total_actual = sum(item.actual_cost for item in costs_list)
    overall_variance = total_budgeted - total_actual

    context = {
        'costs': costs_list,
        'totals': {
            'budget': total_budgeted,
            'actual': total_actual,
            'variance': overall_variance
        },
        'active_section': 'cost_monitoring' # Sidebar highlighters anchor parameter
    }
    return render(request, "operations_planning/costmonitoring.html", context)


from .models import ChangePlan

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def change_plans_view(request):
    """
    📐 SCHEMA COMPLIANT CHANGE PLANS MANAGEMENT ENGINE:
    GET: Compiles all architecture change logs chronologically.
    POST: Processes edits, updates, and creation commands matching your schema choices.
    """
    current_user = request.user

    # 🎯 FIXED DATABASE QUERY: Pulls all records unconditionally to resolve the FieldError crash,
    # since your model doesn't track a 'user' or 'employee' column!
    plans_list = ChangePlan.objects.all().order_by('-created_at')

    if request.method == "POST":
        selected_id = request.POST.get("selected_id")
        project_id = request.POST.get("project_id") or request.POST.get("projectId")
        change_desc = request.POST.get("change_description") or request.POST.get("changeDescription")
        impact = request.POST.get("impact", "Low")
        effective_date = request.POST.get("effective_date") or request.POST.get("effectiveDate")

        # Handle Status validation cleanly based on user workspace authorization
        if current_user.role in ['admin', 'hr']:
            form_status = request.POST.get("status", "Pending")
        else:
            form_status = "Pending"  # Enforces safe default states for non-admins

        clean_date = effective_date if effective_date else None

        try:
            if selected_id:  # Edit / Update path logic block
                plan = get_object_or_404(ChangePlan, id=selected_id)
                plan.project_id = project_id
                plan.change_description = change_desc
                plan.impact = impact
                plan.status = form_status
                plan.effective_date = clean_date
                plan.save()
                messages.success(request, 'Change plan updated successfully!')
                
            else:  # Create Mode (Matches your Mongoose router.post layout)
                # 🎯 FIXED PAYLOAD: Uses only your model's real column fields to avoid crashes!
                ChangePlan.objects.create(
                    project_id=project_id,
                    change_description=change_desc,
                    impact=impact,
                    status=form_status,
                    effective_date=clean_date
                )
                messages.success(request, 'Change plan filed successfully!')
                
        except Exception as e:
            messages.error(request, f'Failed to process change plan record: {e}')

        return redirect('change_plans')

    context = {
        'plans': plans_list,
        'current_role': current_user.role,  # Passed to toggle status dropdown visibility safely
        'active_section': 'change_plans',
        'current_date': timezone.now().date().strftime('%Y-%m-%d')
    }
    return render(request, "operations_planning/change_plan_manager.html", context)



def delete_change_plan_view(request, plan_id):
    """
    Handles removing filed change entries from the grid database rows.
    """
    plan = get_object_or_404(ChangePlan, id=plan_id)
    plan.delete()
    messages.success(request, 'Change plan deleted successfully!')
    return redirect('change_plans')



from .models import Policy

def policy_hub_view(request):
    """
    MATCHES Mongoose: router.get('/policies') and router.post('/policies')
    Provides backend data loops and category metrics tracking for summary cards.
    """
    # 1. Matches: router.get('/policies') -> Fetch all policies ordered by newest first
    policies_list = Policy.objects.all().order_by('-created_at')

    # Replicate your frontend categories tracking list array exactly
    categories_list = ['HR', 'IT', 'Travel', 'Security', 'Finance', 'General']
    
    # Pre-calculate totals for your stats cards list loop block matching React .filter().length
    category_counts = []
    for cat in categories_list:
        category_counts.append({
            'name': cat,
            'count': policies_list.filter(category=cat).count(),
            # Match the dynamic icon class mapping switch rule from your React markup
            'icon': 'fa-user-tie' if cat == 'HR' else ('fa-laptop-code' if cat == 'IT' else 'fa-folder')
        })

    # 2. Matches: router.post('/policies') -> Process incoming frontend payload forms data
    if request.method == "POST":
        # Extract fields matching your frontend parameters
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category", "General")
        version = request.POST.get("version", "1.0")
        effective_date = request.POST.get("effective_date")

        try:
            # Save record cleanly matching your model field constraints mapping names
            Policy.objects.create(
                policy_name=title,            # Map frontend title to model layout path
                category=category,
                version=version,
                effective_date=effective_date if effective_date else timezone.now().date(),
                document_path=description     # Save form description value inside layout row data space
            )
            messages.success(request, 'Policy added successfully')
        except Exception as e:
            messages.error(request, f'Failed to add policy: {e}')
            
        return redirect('policy_hub')

    context = {
        'policies': policies_list,
        'total_count': policies_list.count(),
        'category_stats': category_counts,
        'categories': categories_list,
        'current_date': timezone.now().date().strftime('%Y-%m-%d'),
        'active_section': 'policy_hub'
    }
    return render(request, "operations_planning/policyhub.html", context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Certification
from django.contrib.auth import get_user_model

User = get_user_model()

def certification_management_view(request):
    """
    MATCHES Mongoose: router.get('/certifications') and router.post('/certifications') / router.put('/:id')
    Accepts both legacy and model-level key variations safely.
    """
    # 1. MATCHES: router.get('/certifications') with populate join mappings
    certs_list = Certification.objects.all().select_related('employee').order_by('-created_at')
    employees = User.objects.filter(is_active=True)

    # 2. MATCHES: router.post() and router.put() incoming payload forms handlers
    if request.method == "POST":
        selected_id = request.POST.get("selected_id")
        emp_id = request.POST.get("employee_id") or request.POST.get("employeeId")
        
        # Exact field fallback maps from your Node layout: certData structural object
        cert_name = request.POST.get("certification_name") or request.POST.get("certificationName") or request.POST.get("name")
        provider = request.POST.get("provider") or request.POST.get("issuingOrganization")
        comp_date = request.POST.get("completion_date") or request.POST.get("completionDate") or request.POST.get("issueDate")
        validity_date = request.POST.get("validity") or request.POST.get("expiryDate")
        form_status = request.POST.get("status", "Active")

        # Convert empty strings to clean SQL NULL types natively
        clean_comp = comp_date if comp_date else None
        clean_validity = validity_date if validity_date else None

        try:
            employee_obj = User.objects.get(id=emp_id)

            if selected_id:  
                # MATCHES: router.put('/certifications/:id') -> findByIdAndUpdate
                cert = get_object_or_404(Certification, id=selected_id)
                cert.employee = employee_obj
                cert.certification_name = cert_name
                cert.provider = provider
                cert.completion_date = clean_comp
                cert.validity = clean_validity
                cert.status = form_status
                cert.save()
                messages.success(request, 'Certification record updated successfully!')
            else:  
                # MATCHES: router.post('/certifications') -> new Certification().save()
                Certification.objects.create(
                    employee=employee_obj,
                    certification_name=cert_name,
                    provider=provider,
                    completion_date=clean_comp,
                    validity=clean_validity,
                    status=form_status
                )
                messages.success(request, 'Certification record added successfully!')
                
        except User.DoesNotExist:
            messages.error(request, 'Selected employee profile could not be verified.')
        except Exception as e:
            messages.error(request, f'Failed to process transaction logic: {e}')

        return redirect('certifications')

    context = {
        'certs': certs_list,
        'employees': employees,
        'active_section': 'certifications'
    }
    return render(request, "operations_planning/certifications.html", context)


# Inside apps/operations_planning/views.py

def delete_certification_view(request, cert_id):
    """
    MATCHES Mongoose: router.delete('/certifications/:id') -> findByIdAndDelete
    Permanently deletes a certification entry from the database.
    """
    # 1. Look up the specific row or return a 404 page if missing
    cert = get_object_or_404(Certification, id=cert_id)
    
    # 2. Replicates findByIdAndDelete execution
    cert.delete()
    
    # 3. Flashes a green alert notification toast banner to the UI layout
    messages.success(request, 'Certification deleted successfully!')
    
    # 4. Redirects the worker safely back to the clean dashboard matrix table loop
    return redirect('certifications')
