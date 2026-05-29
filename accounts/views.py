import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings

# GoDaddy Credentials (to be fetched in dashboard)
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
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            
    return render(request, 'accounts/auth.html')

def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, 'accounts/auth.html')
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()
        
        login(request, user)
        return redirect('dashboard')
        
    return redirect('login') 

def inbox_login_ajax(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validate against GoDaddy credentials
        if email == GODADDY_EMAIL and password == GODADDY_PASSWORD:
            otp = str(random.randint(100000, 999999))
            request.session['inbox_otp'] = otp
            
            try:
                # Send OTP specifically to the Gmail account
                send_mail(
                    'Secure Inbox OTP Verification',
                    f'Your verification code for {email} is: {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [OTP_RECEIVER_EMAIL],
                    fail_silently=False,
                )
                return JsonResponse({'status': 'success', 'message': f'OTP sent to {OTP_RECEIVER_EMAIL}'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Email Error: {str(e)}'})
        
        return JsonResponse({'status': 'error', 'message': 'Invalid GoDaddy email or password.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

from imap_tools import MailBox, A

import json

def dashboard_view(request):
    if not request.session.get('inbox_authenticated'):
        return redirect('login')

    emails = []
    error_message = None

    try:
        with MailBox('imap.secureserver.net').login(GODADDY_EMAIL, GODADDY_PASSWORD, 'INBOX') as mailbox:
            # Fetch latest 100 email headers (fast)
            for msg in mailbox.fetch(limit=100, reverse=True):
                emails.append({
                    'uid': msg.uid, # Unique ID for fetching content later
                    'subject': msg.subject or "(No Subject)",
                    'from': msg.from_ or "Unknown Sender",
                    'date': msg.date.strftime("%b %d"),
                    'snippet': msg.text[:100] if msg.text else "",
                })
    except Exception as e:
        error_message = f"GoDaddy IMAP Error: {str(e)}"

    return render(request, 'accounts/dashboard.html', {
        'emails': emails,
        'error_message': error_message,
        'email_user': GODADDY_EMAIL
    })

def fetch_email_content_ajax(request):
    uid = request.GET.get('uid')
    if not uid or not request.session.get('inbox_authenticated'):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    try:
        with MailBox('imap.secureserver.net').login(GODADDY_EMAIL, GODADDY_PASSWORD, 'INBOX') as mailbox:
            # Find the specific email by UID
            for msg in mailbox.fetch(A(uid=uid)):
                return JsonResponse({
                    'status': 'success', 
                    'body': msg.text or "(No content)",
                    'html': msg.html or "" # Support HTML emails too!
                })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Email not found'})

def send_email_ajax(request):
    if not request.session.get('inbox_authenticated'):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    if request.method == "POST":
        recipient = request.POST.get('to')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not recipient or not subject or not message:
            return JsonResponse({'status': 'error', 'message': 'All fields are required.'})

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )
            return JsonResponse({'status': 'success', 'message': 'Email sent successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def verify_otp_ajax(request):
    if request.method == "POST":
        user_otp = request.POST.get('otp')
        saved_otp = request.session.get('inbox_otp')

        if user_otp and user_otp == saved_otp:
            request.session['inbox_authenticated'] = True
            del request.session['inbox_otp']
            # Return the correct redirect URL for the dashboard
            return JsonResponse({'status': 'success', 'redirect_url': '/dashboard/'})
        
        return JsonResponse({'status': 'error', 'message': 'Incorrect OTP code.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})