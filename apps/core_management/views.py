from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import get_user_model
# from apps.core_management.decorators import allowed_roles

User = get_user_model()



@login_required
def update_employee_profile_view(request, employee_id):
    """
    MATCHES Mongoose: router.put('/:id') -> updates data straight inside your unified table rows
    """
    check_admin_hr_clearance(request.user)
    
    if request.method == "POST":
        # Target locate the root user instance matching your tracking primary key parameters
        target_employee = get_object_or_404(User, id=employee_id, role='employee')
        
        # Save updates directly to your model fields attributes maps
        target_employee.full_name = request.POST.get("fullName")
        target_employee.email = request.POST.get("email")
        target_employee.designation = request.POST.get("designation")
        target_employee.department = request.POST.get("department")
        target_employee.phone_number = request.POST.get("phone_number")
        target_employee.emp_code = request.POST.get("emp_code")
        target_employee.save()

        messages.success(request, 'Employee directory dashboard data logs updated successfully!')
        
    return redirect('employee_directory')




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q



User = get_user_model()

def user_management_view(request):
    """
    MATCHES Mongoose: fetchUsers() [GET] and handleSubmit() [POST]
    Handles real-time search querying and dynamic user creation/modification.
    """
    # 1. READ PIPELINE: Extract query variables matching React filter inputs
    search_term = request.GET.get('search', '').strip()
    role_filter = request.GET.get('role', 'all')

    # Base queryset for global directory logging
    all_system_users = User.objects.all()

    # =========================================================================
    # 🔧 CRITICAL FIX: Added execution parentheses () onto your .count() calls!
    # =========================================================================
    stats = {
        'total': all_system_users.count(),
        'admin': all_system_users.filter(role='admin').count(),
        'hr': all_system_users.filter(role='hr').count(),
        'employee': all_system_users.filter(role='employee').count(),
        'bgv_officer': all_system_users.filter(role='bgv_officer').count() # Fixed syntax bug line
    }

    # Apply database text matching filters (Replaces client-side filterUsers())
    filtered_queryset = all_system_users

    if search_term:
        filtered_queryset = filtered_queryset.filter(
            Q(full_name__icontains=search_term) | 
            Q(email__icontains=search_term) |
            Q(username__icontains=search_term)
        )

    if role_filter != 'all':
        filtered_queryset = filtered_queryset.filter(role=role_filter)

    # Replicate newest-first date ordering sorting row records sequence
    users_list = filtered_queryset.order_by('-date_joined')

    # 2. WRITE/MUTATE PIPELINE: Handles User additions and edits in a single POST channel
    if request.method == "POST" and "user_form_submit" in request.POST:
        selected_id = request.POST.get("selected_id")
        email = request.POST.get("email", "").strip()
        
        # ALIGNMENT FIXED: Replaced "fullName" with "full_name" or "fullName" to support both layout variables keys
        full_name = (request.POST.get("fullName") or request.POST.get("full_name", "")).strip()
        role = request.POST.get("role", "employee")
        password = request.POST.get("password")

        try:
            if selected_id:  
                # MATCHES Mongoose: router.put('/users/:id') -> findByIdAndUpdate
                target_user = get_object_or_404(User, id=selected_id)
                target_user.email = email
                target_user.full_name = full_name
                target_user.role = role
                
                # Setup core internal flags matching enterprise dashboard privileges
                # ALIGNMENT FIXED: Granting BGV Officers staff panel privileges natively
                target_user.is_superuser = (role == 'admin')
                target_user.is_staff = (role in ['hr', 'admin', 'bgv_officer'])
                
                # Replicates: if (!updateData.password) { delete updateData.password; }
                if password and password.strip():
                    target_user.set_password(password)
                    
                target_user.save()
                messages.success(request, 'User updated successfully')
            else:  
                # MATCHES Mongoose: router.post('/create-user') -> unique validation block
                if User.objects.filter(email__iexact=email).exists():
                    messages.error(request, 'User already exists')
                    return redirect('user_management')

                # Replicates initial default parameters assignment keys
                generated_username = email.split('@')[0]
                new_user = User.objects.create_user(
                    username=generated_username,
                    email=email,
                    full_name=full_name,
                    role=role,
                    is_superuser=(role == 'admin'),
                    is_staff=(role in ['hr', 'admin', 'bgv_officer']),
                    step=20 # Bypasses onboarding wizard flow steps constraints maps
                )
                if password and password.strip():
                    new_user.set_password(password)
                    new_user.save()
                    
                messages.success(request, 'User created successfully')
                
        except Exception as e:
            messages.error(request, f'Operation execution failed: {e}')

        return redirect('user_management')

    # Map database row outputs directly to your expected template loops keys context definitions
    processed_users = []
    for u in users_list:
        processed_users.append({
            'id': u.id,
            'email': u.email,
            'fullName': u.full_name or u.username,
            'role': u.role or 'employee'
        })

    context = {
        'users': processed_users,
        'stats': stats,
        'searchTerm': search_term,
        'roleFilter': role_filter,
        'active_section': 'user_management'
    }
    return render(request, "core_management/usermanagement.html", context)


@login_required
def delete_user_view(request, user_id):
    """
    MATCHES Mongoose: router.delete('/users/:id') -> findByIdAndDelete
    """
    if request.method == "POST":
        target_user = get_object_or_404(User, id=user_id)
        
        # Enforce security bounds protection rule configuration block
        if target_user.role == 'admin' or target_user.is_superuser:
            messages.error(request, 'Security Violation: Deletion of root administrative profiles is prohibited.')
        else:
            target_user.delete()
            messages.success(request, 'User deleted successfully')
            
    return redirect('user_management')



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

def check_admin_hr_clearance(user):
    """
    Enforces application barrier access controls.
    Replicates legacy rule: if (req.session.role !== 'admin' && req.session.role !== 'hr')
    """
    assigned_role = getattr(user, 'role', 'employee')
    if assigned_role not in ['admin', 'hr'] and not user.is_superuser:
        raise PermissionDenied("Access Denied: Administrative or HR permissions required.")


@login_required
def consolidated_employees_view(request):
    """
    MATCHES React: EmployeeManager summary layout
    Lists employee application entries and processes fallback insertions.
    """
    check_admin_hr_clearance(request.user)

    # Fetch only users with role 'employee' within your single-table configuration
    employees_queryset = User.objects.filter(role='employee').order_by('-date_joined')

    # Replicate your frontend .reduce() / .filter() calculations variables
    total_users = employees_queryset.count()
    total_completed = employees_queryset.filter(step__gte=10).count()
    total_pending = total_users - total_completed

    # Form Submission Handler matching React handleCreateUser()
    if request.method == "POST" and "create_employee_submit" in request.POST:
        email = request.POST.get("email", "").strip()
        full_name = request.POST.get("fullName", "").strip()
        password = request.POST.get("password") or "Welcome@123"
        role = request.POST.get("role", "employee")
        authority = request.POST.get("authorityLevel", "")

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'User account already exists inside the database!')
        else:
            try:
                generated_username = email.split('@')[0]
                new_user = User.objects.create_user(
                    username=generated_username,
                    email=email,
                    full_name=full_name,
                    role=role,
                    authority_level=authority,
                    step=1  # Default startup progress landmark checkpoint configuration value
                )
                new_user.set_password(password)
                new_user.save()
                messages.success(request, 'User Created Successfully!')
            except Exception as e:
                messages.error(request, f'Failed to create user account: {e}')
        
        return redirect('employee_directory')

    # Inject explicit custom checking flags into rows array mapping loops for fast template loads
    processed_employees = []
    for emp in employees_queryset:
        processed_employees.append({
            'id': emp.id,
            'fullName': emp.full_name or emp.username,
            'email': emp.email,
            'role': emp.role,
            'authority_level': emp.authority_level,
            'step': emp.step,
            'updated_at': emp.updated_at,
            'isComplete': emp.step >= 10  # Match exact step tracking check parameters rule
        })

    context = {
        'employees': processed_employees,
        'stats': {
            'total': total_users,
            'completed': total_completed,
            'pending': total_pending
        },
        'active_section': 'employee_directory'
    }
    return render(request, "core_management/employeedirectory.html", context)


@login_required
def employee_ajax_detail_view(request, employee_id):
    """
    MATCHES React Component: EmployeeDetails drawer inspector
    Returns multi-form parameters as a clean nested JSON response structure.
    """
    try:
        check_admin_hr_clearance(request.user)
        emp = User.objects.get(id=employee_id, role='employee')
        
        # Build safe dictionary outputs ensuring fallback values mirror your script's template parameters
        data = {
            'success': True,
            'email': emp.email,
            'role': emp.role,
            'authorityLevel': emp.authority_level or 'Standard Tier',
            'step': emp.step,
            'dateJoined': emp.date_joined.strftime('%m/%d/%Y'),
            
            # Safe unpack checks for your nested JSON field form applications fields parameters maps
            'personal': emp.personal_details or {},
            'address': emp.address_details or {},
            'education': emp.education_history or [],
            'visas': emp.visa_history or [],
            'familyDetails': emp.family_details or {},
            'dobDetail': emp.dob_verification or {},
            'form16': emp.form16_records or [],
            'appForms': emp.passport_details or {},
            'verifyInfo': emp.verify_info or {}
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee application file missing'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Client

@login_required
def client_management_view(request):
    """
    MATCHES Mongoose: router.get('/') and router.post('/')
    Fetches client arrays ordered by newest first and computes global stats.
    """
    # 1. READ ROUTE: Matches Mongoose Client.find().sort({ createdAt: -1 })
    clients_list = Client.objects.all().order_by('-created_at')

    # Replicate React metric aggregation utilities natively on the server side
    total_clients = clients_list.count()
    total_contract_value = sum(item.contract_value for item in clients_list)

    # 2. CREATE ROUTE: Matches Mongoose router.post('/')
    if request.method == "POST":
        client_name = request.POST.get("client_name")
        industry = request.POST.get("industry")
        contact_person = request.POST.get("contact_person")
        contract_value = request.POST.get("contract_value", 0)
        status = request.POST.get("status", "Active")

        try:
            # Commits form data values straight to your model field columns layout
            Client.objects.create(
                client_name=client_name,
                industry=industry,
                contact_person=contact_person,
                contract_value=contract_value if contract_value else 0.00,
                status=status
            )
            messages.success(request, 'Client added successfully')
        except Exception as e:
            messages.error(request, f'Failed to add client record: {e}')
            
        return redirect('client_management')

    context = {
        'clients': clients_list,
        'stats': {
            'total': total_clients,
            'value': total_contract_value
        },
        'active_section': 'client_management'
    }
    return render(request, "core_management/clientmanagement.html", context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ProductClient, Client

@login_required
def product_clients_view(request):
    """
    MATCHES Mongoose: router.get('/product-clients') and router.post('/product-clients') / router.put('/:id')
    Orchestrates reading client arrays, populating relations, and managing data form submissions.
    """
    # 1. READ ROUTE: Matches Mongoose ProductClient.find().populate('clientId')
    products_list = ProductClient.objects.all().select_related('client').order_by('-created_at')
    active_clients = Client.objects.all().order_by('client_name')

    # 2. WRITE/MUTATE ROUTE: Handles standard creation and editing states in one entry point
    # Inside apps/operations_planning/views.py -> product_clients_view function

    if request.method == "POST":
        selected_id_raw = request.POST.get("selected_id", "").strip()
        selected_id = int(selected_id_raw) if selected_id_raw.isdigit() else None
        
        # FIX: Safety bridge fallback keys to catch whatever name attribute is in your HTML form
        product_id = request.POST.get("product_id") or request.POST.get("product_id_code") or request.POST.get("productId")
        product_name = request.POST.get("product_name") or request.POST.get("productName")
        
        client_id_raw = request.POST.get("client_id", "").strip() or request.POST.get("clientId", "").strip()
        client_id = int(client_id_raw) if client_id_raw.isdigit() else None
        
        license_type = request.POST.get("license_type") or request.POST.get("licenseType") or "Standard"
        start_date = request.POST.get("start_date") or request.POST.get("startDate")
        end_date = request.POST.get("end_date") or request.POST.get("endDate")
        support_level = request.POST.get("support_level") or request.POST.get("supportLevel") or "L1"

        clean_start = start_date if start_date else None
        clean_end = end_date if end_date else None

        try:
            client_obj = None
            if client_id:
                client_obj = Client.objects.get(id=client_id)

            if selected_id:  # Edit Mode
                prod_record = get_object_or_404(ProductClient, id=selected_id)
                prod_record.product_id = product_id
                prod_record.product_name = product_name  # Commits correctly now!
                prod_record.client = client_obj
                prod_record.license_type = license_type
                prod_record.start_date = clean_start
                prod_record.end_date = clean_end
                prod_record.support_level = support_level
                prod_record.save()
                messages.success(request, 'Product client link updated successfully!')
            else:  # Create Mode
                ProductClient.objects.create(
                    product_id=product_id,
                    product_name=product_name,  # Commits correctly now!
                    client=client_obj,
                    license_type=license_type,
                    start_date=clean_start,
                    end_date=clean_end,
                    support_level=support_level
                )
                messages.success(request, 'Product client link created successfully!')
                
        except Client.DoesNotExist:
            messages.error(request, 'Failed to process link: Selected client owner does not exist.')
        except Exception as e:
            messages.error(request, f'Failed to commit records: {e}')
            
        return redirect('product_clients')


    context = {
        'products': products_list,
        'clients': active_clients,
        'active_section': 'product_clients'
    }
    return render(request, "core_management/productclients.html", context)


@login_required
def delete_product_client_view(request, record_id):
    """
    MATCHES Mongoose: router.delete('/product-clients/:id') -> findByIdAndDelete
    """
    if request.method == "POST":
        prod_record = get_object_or_404(ProductClient, id=record_id)
        prod_record.delete()
        messages.success(request, 'Licensed product record removed successfully!')
        
    return redirect('product_clients')
