from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def personal_info_dashboard_view(request):
    """
    GET: Reads the active user row instance from the secure session cookies,
    and forwards their nested personal_details JSONField directly onto the detail screen.
    """
    # request.user contains the full single-table row model mapping natively
    context = {
        'employee': request.user,
        'active_section': 'personal_information_sidebar' # Anchors your sidebar active class highlight
    }
    return render(request, 'personal_information/personal_info_detail.html', context)


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

@login_required
def profile_photo_setup_view(request):
    """
    GET: Renders the premium circular file dropzone interface workspace screen.
    """
    context = {
        'employee': request.user,
        'active_section': 'profile_photo_sidebar' # Highlights your sidebar navigation tab active color
    }
    return render(request, 'personal_information/photo_setup.html', context)


@login_required
@csrf_protect # 🔒 Enforces explicit CSRF protection security checks on file multi-part streams
def api_upload_profile_photo_later_view(request):
    """
    POST: Processes the binary image payload dispatched from your file selector dropzone,
    writes the file asset to disk, and updates your user model profile photo column link.
    """
    if request.method == "POST":
        current_employee = request.user
        
        # Look for the raw file binary payload matching your input name="profile_photo"
        if request.FILES.get("profile_photo"):
            
            # 1. Mount the file blob onto the model property column handler channels
            current_employee.profile_photo = request.FILES["profile_photo"]
            
            # 2. Commit to local storage disk drive to write the file and generate a permanent URL path string
            current_employee.save()
            
            messages.success(request, "Your formal biometric badge headshot has been securely saved and synchronized!")
            return redirect('personal_info_dashboard') # Smoothly drops them back onto their profile portfolio summary desk
            
        messages.error(request, "File upload failed. No valid image asset was detected inside the form stream.")
        return redirect('profile_photo_setup')
        
    return JsonResponse({"error": "Method HTTP not allowed. Access via secure POST channels only."}, status=405)

# Open apps/personal_information/views.py

import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

@login_required
def verification_vault_dashboard_view(request):
    """
    GET: Renders your 4-Document Verification interface screen.
    """
    context = {
        'employee': request.user,
        'active_section': 'verification_vault_sidebar'
    }
    return render(request, 'personal_information/documents_vault.html', context)


# Open apps/personal_information/views.py -> Replace your upload function with this:

@login_required
@csrf_protect
def upload_verification_document_api(request):
    """
    POST: Processes a single file upload stream dynamically based on form fields.
    Includes full support for structural identity documents, academic marksheets,
    and unified text/file passport registration payloads.
    """
    if request.method == "POST":
        employee = request.user
        file_saved = False

        # 📄 1. CHECK IDENTITY MEDIA DROPS
        if request.FILES.get("pan_card_doc"):
            employee.pan_card_doc = request.FILES["pan_card_doc"]
            file_saved = True
            messages.success(request, "PAN Card uploaded successfully!")

        elif request.FILES.get("aadhar_card_doc"):
            employee.aadhar_card_doc = request.FILES["aadhar_card_doc"]
            file_saved = True
            messages.success(request, "Aadhar Card uploaded successfully!")

        # 📄 2. CHECK ACADEMIC MEDIA DROPS
        elif request.FILES.get("tenth_marksheet_doc"):
            employee.tenth_marksheet_doc = request.FILES["tenth_marksheet_doc"]
            file_saved = True
            messages.success(request, "10th Marksheet uploaded successfully!")

        elif request.FILES.get("twelfth_marksheet_doc"):
            employee.twelfth_marksheet_doc = request.FILES["twelfth_marksheet_doc"]
            file_saved = True
            messages.success(request, "12th Marksheet uploaded successfully!")

        # 🎯 3. NEW: CHECK PASSPORT PAYLOADS (FILE AND TEXT FIELD COMBINATIONS)
        elif request.FILES.get("passport_doc") or "passport_number" in request.POST:
            
            # Extract and update file if a physical asset exists in multipart binary stream
            if request.FILES.get("passport_doc"):
                employee.passport_doc = request.FILES["passport_doc"]
            
            # Enforce schema security fallback initializers for your JSON field rows
            if not employee.personal_details or not isinstance(employee.personal_details, dict):
                employee.personal_details = {}
            if "hr_compliance" not in employee.personal_details:
                employee.personal_details["hr_compliance"] = {}

            # Overwrite text data fields maps inside your structured JSON matrix
            employee.personal_details["hr_compliance"]["passport_number"] = request.POST.get("passport_number", "").strip() or "N/A"
            employee.personal_details["hr_compliance"]["passport_expiry"] = request.POST.get("passport_expiry_date", "").strip() or "N/A"
            
            file_saved = True
            messages.success(request, "Passport profile vitals and document copy saved successfully!")

        # Final Database Write Actions Handshake
        if file_saved:
            employee.save() # Writes files to hard drive and updates file path strings inside SQLite in one step
        else:
            messages.error(request, "Upload operation failed. No valid file payload or input data detected inside the request stream.")

        return redirect('upload_docs_tab')
        
    return redirect('upload_docs_tab')



@login_required
def preview_verification_document_view(request, doc_type):
    """
    GET: Streams an inline file preview directly inside a new browser tab.
    """
    employee = request.user
    file_field = None

    if doc_type == 'pan': file_field = employee.pan_card_doc
    elif doc_type == 'aadhar': file_field = employee.aadhar_card_doc
    elif doc_type == '10th': file_field = employee.tenth_marksheet_doc
    elif doc_type == '12th': file_field = employee.twelfth_marksheet_doc

    if not file_field or not file_field.name:
        raise Http404("Document file asset is missing or unuploaded.")

    abs_path = file_field.path
    if not os.path.exists(abs_path):
        raise Http404("File missing from structural disk storage system.")

    ext = os.path.splitext(abs_path)[1].lower()
    mime = "application/pdf"
    if ext in ['.jpg', '.jpeg']: mime = "image/jpeg"
    elif ext == '.png': mime = "image/png"

    with open(abs_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=mime)
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(abs_path)}"'
        return response



# Open apps/personal_information/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def upload_documents_workspace_view(request):
    """
    GET: Renders the active workspace containing the 4 upload dropzones
    matching your PAN, Aadhar, 10th, and 12th card layout matrix.
    """
    return render(request, 'personal_information/upload_docs_tab.html', {
        'employee': request.user,
        'active_section': 'upload_docs_sidebar'
    })

@login_required
def view_documents_directory_view(request):
    """
    GET: Renders the read-only audit folder workspace displaying status badges 
    and secure inline 'Open Live Preview' tab buttons.
    """
    return render(request, 'personal_information/view_docs_tab.html', {
        'employee': request.user,
        'active_section': 'view_docs_sidebar'
    })



# Open apps/personal_information/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def standalone_passport_details_view(request):
    """
    GET: Renders a dedicated dashboard page strictly for displaying 
    the employee's passport text parameters and verified attachment.
    """
    return render(request, 'personal_information/passport_detail_page.html', {
        'employee': request.user,
        'active_section': 'passport_details_view_sidebar' # Highlights this unique sidebar item
    })







from django.contrib import messages
from django.conf import settings 

from django.core.files.storage import FileSystemStorage

def education_certification_workspace_view(request):
    """
    GET: Fetches and displays the logged-in candidate's historical academic data log list matrix.
    POST: Extracts data entry fields and appends a new qualification node row block to the profile dictionary.
    """
    employee = request.user

    if request.method == "POST":
        subtype = request.POST.get("subtype", "").strip()
        begin_date = request.POST.get("begin_date", "").strip()
        end_date = request.POST.get("end_date", "").strip()
        details = request.POST.get("details", "").strip()
        cert_file = request.FILES.get("cert_file")

        # 🎯 VALIDATION GATEWAY: Enforce structural entry criteria checks on your 7 exact types
        valid_subtypes = [
            "Secondary", "Senior Secondary", "Graduation", 
            "PG", "Diploma", "Tech Certificates", "Internship Certificates"
        ]
        if subtype not in valid_subtypes:
            messages.error(request, "Invalid qualification subtype layer detected.")
            return redirect('education_certification_workspace')

        # Initialize JSON schema fallbacks cleanly within the user row record model
        if not employee.personal_details or not isinstance(employee.personal_details, dict):
            employee.personal_details = {}
        if "education_records" not in employee.personal_details:
            employee.personal_details["education_records"] = []

        # Stream attachment files to media drive paths dynamically if a document scan was attached
        file_url = ""
        if cert_file:
            # Leverage a localized FileSystemStorage instance to isolate attachments securely
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'education_certs'))
            filename = fs.save(f"user_{employee.id}_{subtype.lower().replace(' ', '_')}_{cert_file.name}", cert_file)
            file_url = f"{settings.MEDIA_URL}education_certs/{filename}"

        # Construct the new data row entry parameter node payload map
        new_record = {
            "subtype": subtype,
            "begin_date": begin_date,
            "end_date": end_date,
            "details": details,
            "file_url": file_url
        }

        # Commit payload straight up into the flexible user dictionary table parameters column
        employee.personal_details["education_records"].append(new_record)
        employee.save()

        messages.success(request, f"Successfully committed {subtype} credentials to your academic log files!")
        return redirect('education_certification_workspace')

    # Read tracking arrays from user model JSON block parameters to load onto your front table screen
    records = []
    if employee.personal_details and isinstance(employee.personal_details, dict):
        records = employee.personal_details.get("education_records", [])

    return render(request, 'personal_information/education_vault.html', {
        'records': records,
        'active_section': 'view_qualifications_sidebar' # 🎯 Lights up your sidebar menu block link dynamically
    })


# Append this to apps/personal_information/views.py


def previous_employer_workspace_view(request):
    """
    GET: Fetches and displays the candidate's structural corporate career timeline history log.
    POST: Processes data entry fields and commits a new employment record row to the JSON parameters column.
    """
    employee = request.user

    if request.method == "POST":
        employer_name = request.POST.get("employer_name", "").strip()
        designation = request.POST.get("designation", "").strip()
        begin_date = request.POST.get("begin_date", "").strip()
        end_date = request.POST.get("end_date", "").strip()
        reason_leaving = request.POST.get("reason_leaving", "").strip()
        exp_file = request.FILES.get("exp_file")

        # Fallback dictionary schema layer initializations
        if not employee.personal_details or not isinstance(employee.personal_details, dict):
            employee.personal_details = {}
        if "previous_employers" not in employee.personal_details:
            employee.personal_details["previous_employers"] = []

        # Stream the career certificate files dynamically to your media directory paths storage
        file_url = ""
        if exp_file:
            # Isolates and secures custom career certificate scans safely inside a subfolder
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'experience_certs'))
            filename = fs.save(f"user_{employee.id}_exp_{exp_file.name}", exp_file)
            file_url = f"{settings.MEDIA_URL}experience_certs/{filename}"

        # Construct the historical data log row parameters node
        new_record = {
            "employer_name": employer_name,
            "designation": designation,
            "begin_date": begin_date,
            "end_date": end_date,
            "reason_leaving": reason_leaving,
            "file_url": file_url
        }

        # Commit payload parameters straight up into the flexible user row data matrix
        employee.personal_details["previous_employers"].append(new_record)
        employee.save()

        messages.success(request, f"Successfully logged career history data row for {employer_name}!")
        return redirect('previous_employer_workspace')

    # Read tracking arrays from user model JSON block parameters to load onto your front table screen
    employer_records = []
    if employee.personal_details and isinstance(employee.personal_details, dict):
        employer_records = employee.personal_details.get("previous_employers", [])

    return render(request, 'personal_information/previous_employer.html', {
        'employer_records': employer_records,
        'active_section': 'previous_employer_sidebar'  # Keeps your sidebar dropdown navigation menu active
    })




# Append this to apps/personal_information/views.py


def family_details_workspace_view(request):
    """
    GET: Fetches and displays the candidate's structural family dependents registry.
    POST: Processes input fields and appends a new family member node block to the JSON column.
    """
    employee = request.user

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        relationship = request.POST.get("relationship", "").strip()
        dob = request.POST.get("dob", "").strip()
        blood_group = request.POST.get("blood_group", "").strip()

        # Initialize JSON schema fallbacks cleanly inside the database user record
        if not employee.personal_details or not isinstance(employee.personal_details, dict):
            employee.personal_details = {}
        if "family_members" not in employee.personal_details:
            employee.personal_details["family_members"] = []

        # Construct the new data row entry payload map
        new_member = {
            "full_name": full_name,
            "relationship": relationship,
            "dob": dob,
            "blood_group": blood_group
        }

        # Commit payload parameters straight up into the flexible user dictionary table parameters column
        employee.personal_details["family_members"].append(new_member)
        employee.save()

        messages.success(request, f"Successfully registered family record for {full_name}!")
        return redirect('family_details')

    # Read tracking arrays from user model JSON block parameters to load onto your front table screen
    family_records = []
    if employee.personal_details and isinstance(employee.personal_details, dict):
        family_records = employee.personal_details.get("family_members", [])

    return render(request, 'personal_information/family_details.html', {
        'family_records': family_records,
        'active_section': 'family_details_sidebar' # 🎯 Lights up your sidebar menu block link dynamically
    })


# Append this to apps/personal_information/views.py

def visa_details_workspace_view(request):
    """
    GET: Fetches and displays the candidate's international immigration portfolio log list.
    POST: Processes form fields and commits a new visa tracking row block to the JSON parameters column.
    """
    employee = request.user

    if request.method == "POST":
        country = request.POST.get("country", "").strip()
        visa_type = request.POST.get("visa_type", "").strip()
        visa_number = request.POST.get("visa_number", "").strip()
        issue_date = request.POST.get("issue_date", "").strip()
        expiry_date = request.POST.get("expiry_date", "").strip()
        visa_file = request.FILES.get("visa_file")

        # Initialize JSON schema fallbacks safely within the user row record model
        if not employee.personal_details or not isinstance(employee.personal_details, dict):
            employee.personal_details = {}
        if "visa_records" not in employee.personal_details:
            employee.personal_details["visa_records"] = []

        # Stream attachment files to media drive paths dynamically if a document scan was uploaded
        file_url = ""
        if visa_file:
            # Isolates and secures custom immigration visa stamp scans safely inside a subfolder
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'visa_docs'))
            filename = fs.save(f"user_{employee.id}_visa_{visa_file.name}", visa_file)
            file_url = f"{settings.MEDIA_URL}visa_docs/{filename}"

        # Construct the new data row entry parameter node payload map
        new_record = {
            "country": country,
            "visa_type": visa_type,
            "visa_number": visa_number,
            "issue_date": issue_date,
            "expiry_date": expiry_date,
            "file_url": file_url
        }

        # Commit payload straight up into the flexible user dictionary table parameters column
        employee.personal_details["visa_records"].append(new_record)
        employee.save()

        messages.success(request, f"Successfully logged visa authorization for {country}!")
        return redirect('visa_details_workspace')

    # Read tracking arrays from user model JSON block parameters to load onto your front table screen
    visa_records = []
    if employee.personal_details and isinstance(employee.personal_details, dict):
        visa_records = employee.personal_details.get("visa_records", [])

    return render(request, 'personal_information/visa_details.html', {
        'visa_records': visa_records,
        'active_section': 'visa_details_sidebar'  # Lights up your sidebar menu block link dynamically
    })




# Open apps/personal_information/views.py
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

@login_required
def id_card_dashboard_view(request):
    """
    🪪 FULL-STACK ROLE DETECTING ID WORKSPACE CENTRAL ROUTER ENGINE:
    GET (Employee): Reads active badge request status tracking records from JSON.
    POST (Employee): Dispatches a brand new request token flag up to the server.
    POST (HR Action): Processes individual 'Approve' or 'Reject' updates on employee rows using clean IDs.
    """
    user = request.user
    
    # =========================================================================
    # 🎯 TARGET TRACK A: USER IS AN ADMIN OR HR MODERATOR
    # =========================================================================
    if user.role in ['admin', 'hr']:
        
        # PROCESS POST HR ACTION: Updates the target database record status parameters
        if request.method == "POST" and "target_employee_id" in request.POST:
            target_emp_id = request.POST.get("target_employee_id")
            action_decision = request.POST.get("action_decision") # 'Approve' or 'Reject'
            
            # Query using native 'id' integer key directly to avoid FieldErrors
            target_employee = get_object_or_404(User, id=target_emp_id)
            
            if not target_employee.personal_details or not isinstance(target_employee.personal_details, dict):
                target_employee.personal_details = {}
                
            if action_decision == "Approve":
                target_employee.personal_details["id_card_request_status"] = "Approved"
                messages.success(request, f"Successfully approved printing pass row for {target_employee.username}!")
            elif action_decision == "Reject":
                target_employee.personal_details["id_card_request_status"] = "Not Requested" # Unlocks form for edits
                messages.warning(request, f"Rejected badge request for {target_employee.username}.")
                
            target_employee.save()
            return redirect('/personal-information/id-card-workspace/')

        # GET REQUEST: Compile all active 'Pending' records into the data grid row list
        pending_requests = []
        all_users = User.objects.all()
        for emp in all_users:
            if emp.personal_details and isinstance(emp.personal_details, dict):
                if emp.personal_details.get("id_card_request_status") == "Pending":
                    photo = "/static/images/default_avatar.png"
                    if emp.profile_photo:
                        photo = emp.profile_photo.url
                        
                    # 🚀 EXTRACTION LOOPS: Pull metrics directly from your verifiable database fields matrix
                    emp_details = emp.personal_details if isinstance(emp.personal_details, dict) else {}
                    
                    # 🎯 FIXED SCHEMA SYNC: Extract from your exact 'identity_demographics' container block!
                    identity_meta = emp_details.get("identity_demographics", {})
                    extracted_dept = identity_meta.get("department", "-")
                    extracted_desg = identity_meta.get("designation", "-")
                    
                    # This will print directly into your running VS Code terminal:
                    print(f"🔍 DEBUG [User: {emp.username}] Dept: {extracted_dept} | Desg: {extracted_desg}")
                    
                    pending_requests.append({
                        "employee_id": emp.id, # Raw integer primary key for safe data transport loops
                        "name": emp.username,
                        
                        # 🎯 100% SCHEMA COMPLIANT: Fetches live strings from database form submissions
                        "department": identity_meta.get("department", "-"),
                        "designation": identity_meta.get("designation", "-"),
                        
                        "photo_url": photo,
                        "request_date": emp_details.get("id_card_request_date", "28-05-2026"),
                        "status": "Pending"
                    })
                    
        return render(request, 'personal_information/hr_id_queue.html', {
            'requests': pending_requests,
            'active_section': 'id_card_management_sidebar'
        })
        
    # =========================================================================
    # 🎯 TARGET TRACK B: USER IS A STANDARD EMPLOYEE / CANDIDATE WORKFLOW
    # =========================================================================
    else:
        if request.method == "POST":
            if not user.personal_details or not isinstance(user.personal_details, dict):
                user.personal_details = {}
                
            # Update tracking status flags to lock the form and beam to HR queue
            user.personal_details["id_card_request_status"] = "Pending"
            user.personal_details["id_card_request_date"] = "28-05-2026" # Logs today's date timestamp
            user.save()
            
            messages.success(request, "Your ID card print request has been securely dispatched to HR services!")
            return redirect('/personal-information/id-card-workspace/')

        # Read the current status out of the profile parameters to display appropriate badge chips
        request_status = "Not Requested"
        if user.personal_details and isinstance(user.personal_details, dict):
            request_status = user.personal_details.get("id_card_request_status", "Not Requested")

        return render(request, 'personal_information/employee_id_request.html', {
            'request_status': request_status,
            'active_section': 'id_card_management_sidebar'
        })






# Append this to apps/personal_information/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def communication_overview_view(request):
    """
    📞 CENTRAL COMMUNICATION OVERVIEW WORKSPACE TRACKER:
    GET: Reads structural timeline channel logs from the user's personal_details JSON.
    POST: Extracts fresh asset metrics and appends a row node to the registry payload array.
    """
    user = request.user

    # GET DATA LOADING PASSTHROUGH LAYER
    # Read tracking arrays directly out of your flexible user model dictionary column
    user_details = user.personal_details if isinstance(user.personal_details, dict) else {}
    communication_records = user_details.get("communication_logs", [])

    if request.method == "POST":
        sub_type = request.POST.get("sub_type", "").strip()
        begin_date = request.POST.get("begin_date", "").strip()
        end_date = request.POST.get("end_date", "").strip() or "Immediate"
        details = request.POST.get("details", "").strip()

        # Initialize JSON schema dictionary block fallbacks safely on the user record
        if not user.personal_details or not isinstance(user.personal_details, dict):
            user.personal_details = {}
        if "communication_logs" not in user.personal_details:
            user.personal_details["communication_logs"] = []

        # Construct the fresh chronological data row payload map
        new_record = {
            "sub_type": sub_type,
            "begin_date": begin_date,
            "end_date": end_date,
            "details": details
        }

        # Commit payload parameters directly up into your flexible user model JSON column
        user.personal_details["communication_logs"].append(new_record)
        user.save()

        messages.success(request, f"Successfully registered {sub_type} allocation timeline!")
        return redirect('/personal-information/communication-overview/')

    context = {
        'comms_records': communication_records,
        'active_section': 'communication_overview_sidebar' # Keeps sidebar reference clean
    }
    return render(request, "personal_information/communication_overview.html", context)


# Append this to apps/personal_information/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def payslip_workspace_view(request):
    """
    💵 FULL-STACK PAYROLL PORTAL WORKSPACE ENGINE:
    HR / Admin: Can filter workers by month and click to generate a custom payslip record.
    Employees: Can only view a read-only tracking list and download their own personal files.
    """
    user = request.user
    selected_month = request.GET.get('month', 'May 2026') # Default dashboard month filter

    # =========================================================================
    # 🎯 TARGET TRACK A: USER IS AN ADMIN OR HR MODERATOR
    # =========================================================================
    if user.role in ['admin', 'hr']:
        
        # PROCESS POST PAYSLIP GENERATION: Commits financial records to the target employee
        if request.method == "POST" and "generate_payslip_trigger" in request.POST:
            target_emp_id = request.POST.get("target_employee_id")
            basic_salary = request.POST.get("basic_salary", "0")
            hra = request.POST.get("hra", "0")
            allowances = request.POST.get("allowances", "0")
            deductions = request.POST.get("deductions", "0")
            target_month = request.POST.get("payroll_month", selected_month)

            # Compute Net Take-Home Pay natively to ensure mathematical calculation accuracy
            try:
                gross = float(basic_salary) + float(hra) + float(allowances)
                net_pay = gross - float(deductions)
            except ValueError:
                net_pay = 0.0

            target_employee = get_object_or_404(User, id=target_emp_id)
            
            # Initialize JSON schema matrix block fallbacks safely on the target user record
            if not target_employee.personal_details or not isinstance(target_employee.personal_details, dict):
                target_employee.personal_details = {}
            if "payslips" not in target_employee.personal_details:
                target_employee.personal_details["payslips"] = []

            # Construct and append the fresh monthly financial payload row node
            new_payslip = {
                "month": target_month,
                "basic_salary": basic_salary,
                "hra": hra,
                "allowances": allowances,
                "deductions": deductions,
                "net_pay": f"{net_pay:.2f}",
                "generated_on": "2026-05-28"
            }
            
            target_employee.personal_details["payslips"].append(new_payslip)
            target_employee.save()

            messages.success(request, f"Payslip successfully generated for {target_employee.username} for {target_month}!")
            return redirect(f"/personal-information/payslips/?month={target_month}")

        # GET: Compile all workers and append their monthly payroll states dynamically
        all_users = User.objects.all()
        employee_payroll_grid = []
        
        for emp in all_users:
            emp_details = emp.personal_details if isinstance(emp.personal_details, dict) else {}
            identity_meta = emp_details.get("identity_demographics", {})
            payslips_list = emp_details.get("payslips", [])

            # Check if this specific employee already has a generated payslip row for the filtered month
            has_payslip = False
            matching_payslip_data = None
            for p in payslips_list:
                if p.get("month") == selected_month:
                    has_payslip = True
                    matching_payslip_data = p
                    break

            employee_payroll_grid.append({
                "id": emp.id,
                "name": emp.username,
                "department": identity_meta.get("department", "-"),
                "designation": identity_meta.get("designation", "-"),
                "has_payslip": has_payslip,
                "payslip_data": matching_payslip_data
            })

        return render(request, 'personal_information/hr_payslip_dashboard.html', {
            'employees': employee_payroll_grid,
            'selected_month': selected_month
        })

    # =========================================================================
    # 🎯 TARGET TRACK B: USER IS A STANDARD EMPLOYEE PORTAL VIEW
    # =========================================================================
    else:
        user_details = user.personal_details if isinstance(user.personal_details, dict) else {}
        my_payslips = user_details.get("payslips", [])
        
        return render(request, 'personal_information/employee_payslip_view.html', {
            'payslips': my_payslips,
            'selected_month': selected_month
        })
