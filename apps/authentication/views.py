import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage


# GoDaddy Credentials (for validation)
GODADDY_EMAIL = "sales@voxlom.com"
GODADDY_PASSWORD = "qwertya@123"

# OTP Receiving Email (Gmail)
OTP_RECEIVER_EMAIL = "iyappanvox3@gmail.com"

def auth_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.last_login is None:

                login(request,user)

                return redirect ('welcome_board')
            
            login(request, user)
            return redirect('employee_dashboard') #--------------------------->
        else:
            messages.error(request, "Invalid email or password.")
            
    return render(request, 'authentication/auth.html')

def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, 'authentication/auth.html')
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()
        
        login(request, user)
        return redirect('employee_dashboard')
        
    return redirect('login') 

def inbox_login_ajax(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email == GODADDY_EMAIL and password == GODADDY_PASSWORD:
            otp = str(random.randint(100000, 999999))
            request.session['inbox_otp'] = otp
            
            try:
                send_mail(
                    'Secure Inbox OTP Verification',
                    f'Your verification code is : {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [OTP_RECEIVER_EMAIL],
                    fail_silently=False,
                )
                return JsonResponse({'status': 'success', 'message': f'OTP sent to {OTP_RECEIVER_EMAIL}'})
            except Exception as e:
                # LOG TO FILE FOR ME TO SEE
                with open('debug_mail.log', 'a') as f:
                    f.write(f"EMAIL ERROR: {str(e)}\n")
                return JsonResponse({'status': 'error', 'message': f'Server Error: Check Logs'})
        
        return JsonResponse({'status': 'error', 'message': 'Invalid GoDaddy email or password.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def verify_otp_ajax(request):
    print("DEBUG: Verify OTP Ajax Called!")
    if request.method == "POST":
        user_otp = request.POST.get('otp')
        saved_otp = request.session.get('inbox_otp')
        print(f"DEBUG: User OTP: {user_otp}, Saved OTP: {saved_otp}")

        if user_otp and user_otp == saved_otp:
            print("DEBUG: OTP Match! Authenticating...")
            request.session['inbox_authenticated'] = True
            del request.session['inbox_otp']
            return JsonResponse({'status': 'success', 'redirect_url': '/dashboard/'})
        
        print("DEBUG: OTP Mismatch!")
        return JsonResponse({'status': 'error', 'message': 'Invalid verification code.'})

def logout_view(request):
    from django.contrib.auth import logout
    logout(request) # Clear standard auth
    request.session.flush() # Clear all custom session data (inbox auth, etc)
    return redirect('login')


def selected_canditate_view (request) :

    return render (request , "authentication/canditate_login.html")


import requests
from django.shortcuts import redirect
from django.conf import settings

def google_login(request):
    # Redirect to Google OAuth
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        "response_type=code&"
        "scope=openid email profile"
    )
    return redirect(google_auth_url)


def google_callback(request):
    # Handle callback from Google
    code = request.GET.get("code")

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    r = requests.post(token_url, data=data)
    tokens = r.json()
    id_token = tokens.get("id_token")

    # TODO: Decode and verify id_token properly (using PyJWT or google-auth)
    # For now, assume valid and redirect to upload page
    return redirect("upload_documents")

def welcome_board(request):
    return render(request,"authentication/welcomeboard.html")


# Open apps/authentication/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required # 🔒 Enforces explicit session protection so employees only modify their own profile row
def candidate_personal_info_form_view(request):
    """
    Handles extracting all 25+ data metrics from your 4-step wizard form,
    packages text fields into the personal_details JSONField, routes physical 
    attachments to local disk channels, and advances their system tracking step.
    """
    # Pull active HR Managers to dynamically populate the reporting dropdown choice list menu
    hr_leads_list = User.objects.filter(role='hr', is_active=True).order_by('first_name', 'username')

    if request.method == "POST" and "onboarding_form_submit" in request.POST:

        
        
        # =========================================================================
        # 📦 1. EXTRACT AND GROUP STEP 1: IDENTITY, CITIZENSHIP & DEMOGRAPHICS
        # =========================================================================
        vitals_payload = {
            "form_of_address": request.POST.get("form_of_address", "").strip(),
            "gender": request.POST.get("gender", "").strip(),
            "first_name": request.POST.get("first_name", "").strip(),
            "last_name": request.POST.get("last_name", "").strip(),
            "certificate_name": request.POST.get("certificate_name", "").strip(),
            "dob": request.POST.get("dob", "").strip(),
            "marital_status": request.POST.get("marital_status", "").strip(),
            "marriage_date": request.POST.get("marriage_date", "").strip() or "-",
            "nationality": request.POST.get("nationality", "").strip(),
            "country_of_birth": request.POST.get("country_of_birth", "").strip(),
            "state_of_birth": request.POST.get("state_of_birth", "").strip(),
            "city_of_birth": request.POST.get("city_of_birth", "").strip(),
            "citizen_status": request.POST.get("citizen_status", "").strip(),
            "dual_citizenship": request.POST.get("dual_citizenship", "").strip(),
            "disability": request.POST.get("disability", "").strip(),
            "disability_category": request.POST.get("disability_category", "").strip() or "-",
            "blood_group": request.POST.get("blood_group", "").strip(),
            "department":request.POST.get("department" ,  "").strip(),
            "designation":request.POST.get("designation" ,"").strip(),
        }

        # =========================================================================
        # 📦 2. EXTRACT AND GROUP STEP 2: RESIDENTIAL & WORKSITE INFRASTRUCTURE
        # =========================================================================
        addresses_payload = {
            "current_address": request.POST.get("current_address", "").strip(),
            "permanent_address": request.POST.get("permanent_address", "").strip(),
            "mailing_address": request.POST.get("mailing_address", "").strip(),
            "office_worksite": request.POST.get("office_worksite", "").strip()
        }

        # =========================================================================
        # 📦 3. EXTRACT AND GROUP STEP 3: EMERGENCY INFRASTRUCTURE PROTOCOL
        # =========================================================================
        emergency_payload = {
            "contact_name": request.POST.get("emergency_contact_name", "").strip(),
            "relationship": request.POST.get("emergency_relationship", "").strip(),
            "phone": request.POST.get("emergency_phone", "").strip(),
            "address": request.POST.get("emergency_address", "").strip()
        }

        # =========================================================================
        # 📦 4. EXTRACT AND GROUP STEP 4: HR ALIGNMENT TIMELINES
        # =========================================================================
        hr_compliance_payload = {
            "reporting_hr_lead_id": request.POST.get("hr_reporting_id", "").strip(),
            "personal_data_begin_date": request.POST.get("personal_data_begin_date", "").strip() or "-",
            "personal_data_end_date": request.POST.get("personal_data_end_date", "").strip() or "-",
            "consent_confirmed": True
        }

        # Fetch active logged-in instance row pointer securely from request session cookies
        employee_profile = request.user

        # =========================================================================
        # 🚀 5. INJECT DICTIONARY MAP STRINGS INTO INDEPENDENT JSONField CONTAINER
        # =========================================================================
        employee_profile.personal_details = {
            "identity_demographics": vitals_payload,
            "addresses": addresses_payload,
            "emergency_contact": emergency_payload,
            "hr_compliance": hr_compliance_payload
        }

        # =========================================================================
        # 📁 6. DISPATCH RAW BIOMETRIC ATTACHMENTS TO THE MODEL COLUMNS DIRECTLY
        # =========================================================================
        if request.FILES.get("profile_photo"):
            employee_profile.profile_photo = request.FILES["profile_photo"]
            
        if request.FILES.get("passport_doc"):
            employee_profile.passport_doc = request.FILES["passport_doc"]
            
        if request.FILES.get("tenth_certificate_doc"):
            employee_profile.tenth_certificate_doc = request.FILES["tenth_certificate_doc"]

        # Advance their corporate tracking lifecycle status flag milestone permanently!
        employee_profile.step = 20  
        
        # Save record. Django automatically stringifies and commits the massive nested dictionary to SQLite!
        employee_profile.save() 

        messages.success(request, "Your background details portfolio has been locked and saved securely inside your corporate record!")
        return redirect('employee_dashboard')

    # If request method evaluation resolves to an asset GET loop, paint the wizard template canvas sheets
    context = {
        'hr_leads': hr_leads_list,
        'active_section': 'onboarding_vitals_form'
    }
    return render(request, "authentication/candidate_personal_form.html", context)
