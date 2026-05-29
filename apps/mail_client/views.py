import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings

from imap_tools import MailBox, A

# GoDaddy Credentials (for IMAP fetching)
GODADDY_EMAIL = "sales@voxlom.com"
GODADDY_PASSWORD = "qwertya@123"

# pyrefly: ignore [missing-import]
from .models import LocalDraft, PinnedEmail, SnoozedEmail, UserSettings
from django.utils import timezone
from datetime import timedelta

def dashboard_view(request):
    if not request.session.get('inbox_authenticated'):
        return redirect('login')

    # Get folder from request, default to INBOX
    requested_folder = request.GET.get('folder', 'INBOX')
    emails = []
    error_message = None
    all_folders = []

    user_settings, _ = UserSettings.objects.get_or_create(
        email_account=GODADDY_EMAIL,
        defaults={'emails_per_page': 50, 'inbox_type': 'default', 'display_density': 'default', 'theme': 'light', 'text_size': 'Normal'}
    )

    try:
        # 1. Handle Local Drafts
        if requested_folder == 'Drafts':
            local_drafts = LocalDraft.objects.all().order_by('-updated_at')
            for d in local_drafts:
                emails.append({
                    'uid': f"local_{d.id}",
                    'subject': d.subject or "(No Subject)",
                    'from': d.recipient or "Draft",
                    'date': d.updated_at.strftime("%b %d"),
                    'snippet': (d.message[:100] if d.message else "") + "...",
                    'is_local': True
                })

        # 2. Handle Snoozed Tab
        if requested_folder == 'Snoozed':
            snoozed = SnoozedEmail.objects.all().order_by('snooze_until')
            for s in snoozed:
                emails.append({
                    'uid': s.uid,
                    'subject': s.subject or "(No Subject)",
                    'from': s.sender or "Unknown",
                    'date': f"Until {s.snooze_until.strftime('%b %d')}",
                    'snippet': f"Snoozed until {s.snooze_until.strftime('%I:%M %p')}",
                    'is_snoozed': True,
                    'folder': s.folder
                })

        # 3. Handle Pinned Tab
        if requested_folder == 'Pinned':
            pinned = PinnedEmail.objects.all().order_by('-created_at')
            for p in pinned:
                emails.append({
                    'uid': p.uid,
                    'subject': p.subject or "(No Subject)",
                    'from': p.sender or "Unknown",
                    'date': "Pinned",
                    'snippet': p.snippet or "Pinned message",
                    'is_pinned': True,
                    'folder': p.folder
                })

        with MailBox('imap.secureserver.net').login(GODADDY_EMAIL, GODADDY_PASSWORD) as mailbox:
            # Smart Folder Detection
            target_folder = requested_folder
            available_folders = [f.name for f in mailbox.folder.list()]
            all_folders = available_folders
            
            # ... (mapping special folders)
            if requested_folder == 'Drafts' and 'Drafts' not in available_folders:
                for f in ['INBOX.Drafts', 'Drafts Folder', 'Draft', 'DRAFTS']:
                    if f in available_folders:
                        target_folder = f
                        break
            elif requested_folder == 'Sent' and 'Sent' not in available_folders:
                for f in ['INBOX.Sent', 'Sent Messages', 'Sent Items', 'SENT']:
                    if f in available_folders:
                        target_folder = f
                        break
            elif requested_folder == 'Spam' and 'Spam' not in available_folders:
                for f in ['INBOX.Spam', 'Junk', 'Junk E-mail', 'SPAM']:
                    if f in available_folders:
                        target_folder = f
                        break
            elif requested_folder == 'Archive' and 'Archive' not in available_folders:
                for f in ['INBOX.Archive', 'All Mail', 'INBOX.All Mail']:
                    if f in available_folders:
                        target_folder = f
                        break
            elif requested_folder == 'Bin' and 'Trash' not in available_folders:
                for f in ['INBOX.Trash', 'Trash', 'Bin', 'Deleted Items', 'DELETED']:
                    if f in available_folders:
                        target_folder = f
                        break
            
            if requested_folder == 'Starred':
                mailbox.folder.set('INBOX')
                for msg in mailbox.fetch(A(flagged=True), limit=user_settings.emails_per_page, reverse=True):
                    emails.append({
                        'uid': msg.uid, 'subject': msg.subject or "(No Subject)", 'from': msg.from_ or "Unknown Sender",
                        'date': msg.date.strftime("%b %d") if msg.date else "N/A", 'snippet': (msg.text[:100] if msg.text else "") + "...",
                        'is_starred': True
                    })
                current_folder = 'INBOX'
            elif requested_folder in ['Snoozed', 'Pinned']:
                current_folder = 'INBOX' # Just for the sidebar highlight
            else:
                mailbox.folder.set(target_folder)
                # Filter out currently snoozed UIDs if viewing INBOX
                snoozed_uids = []
                pinned_uids = []
                if target_folder == 'INBOX':
                    snoozed_uids = list(SnoozedEmail.objects.filter(snooze_until__gt=timezone.now()).values_list('uid', flat=True))
                pinned_uids = list(PinnedEmail.objects.values_list('uid', flat=True))

                for msg in mailbox.fetch(limit=user_settings.emails_per_page, reverse=True):
                    if msg.uid in snoozed_uids:
                        continue
                    emails.append({
                        'uid': msg.uid, 'subject': msg.subject or "(No Subject)", 'from': msg.from_ or "Unknown Sender",
                        'date': msg.date.strftime("%b %d") if msg.date else "N/A", 'snippet': (msg.text[:100] if msg.text else "") + "...",
                        'is_starred': '\\Flagged' in msg.flags,
                        'is_pinned': msg.uid in pinned_uids
                    })
                current_folder = target_folder
    except Exception as e:
        error_message = f"Error: {str(e)}"
        current_folder = requested_folder

    display_name = GODADDY_EMAIL.split('@')[0].capitalize()
    
    return render(request, 'mail_client/dashboard.html', {
        'emails': emails, 'error_message': error_message, 'email_user': GODADDY_EMAIL,
        'display_name': display_name,
        'current_folder': current_folder, 'requested_folder': requested_folder, 'all_folders': all_folders,
        'user_settings': user_settings
    })

def snooze_email_ajax(request):
    if not request.session.get('inbox_authenticated'):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    if request.method == "POST":
        uid = request.POST.get('uid')
        subject = request.POST.get('subject')
        sender = request.POST.get('sender')
        days = int(request.POST.get('days', 1))
        
        until = timezone.now() + timedelta(days=days)
        
        SnoozedEmail.objects.update_or_create(
            uid=uid,
            defaults={
                'subject': subject,
                'sender': sender,
                'snooze_until': until,
                'folder': request.POST.get('folder', 'INBOX')
            }
        )
        return JsonResponse({'status': 'success', 'message': f'Email snoozed until {until.strftime("%b %d")}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def unsnooze_email_ajax(request):
    if not request.session.get('inbox_authenticated'):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    if request.method == "POST":
        uid = request.POST.get('uid')
        if not uid:
            return JsonResponse({'status': 'error', 'message': 'UID required'})
        
        SnoozedEmail.objects.filter(uid=uid).delete()
        return JsonResponse({'status': 'success', 'message': 'Email unsnoozed'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def fetch_email_content_ajax(request):
    uid = request.GET.get('uid')
    folder = request.GET.get('folder', 'INBOX')

    if not uid or not request.session.get('inbox_authenticated'):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    # 1. Handle Local Drafts
    if uid.startswith('local_'):
        try:
            draft_id = uid.replace('local_', '')
            draft = LocalDraft.objects.get(id=draft_id)
            return JsonResponse({
                'status': 'success',
                'subject': draft.subject or "(No Subject)",
                'body': draft.message or "(No content)",
                'html': ""
            })
        except LocalDraft.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Draft not found'})

    # 2. Handle Server Emails
    try:
        with MailBox('imap.secureserver.net').login(GODADDY_EMAIL, GODADDY_PASSWORD, folder) as mailbox:
            for msg in mailbox.fetch(A(uid=uid)):
                return JsonResponse({
                    'status': 'success', 
                    'subject': msg.subject or "(No Subject)",
                    'body': msg.text or "(No content)",
                    'html': msg.html or ""
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

def delete_email_ajax(request):
    if not request.session.get('inbox_authenticated'):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    uid = request.GET.get('uid')
    folder = request.GET.get('folder', 'INBOX')
    if not uid:
        return JsonResponse({'status': 'error', 'message': 'UID required'})

    # 1. Handle Local Draft Deletion
    if uid.startswith('local_'):
        try:
            draft_id = uid.replace('local_', '')
            LocalDraft.objects.filter(id=draft_id).delete()
            return JsonResponse({'status': 'success', 'message': 'Draft deleted locally'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    # 2. Handle Server Deletion
    try:
        with MailBox('imap.secureserver.net').login(GODADDY_EMAIL, GODADDY_PASSWORD, folder) as mailbox:
            mailbox.delete(uid)
            mailbox.expunge()
            return JsonResponse({'status': 'success', 'message': 'Email deleted from server'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
def save_draft_ajax(request):
    if not request.session.get('inbox_authenticated'):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    if request.method == "POST":
        recipient = request.POST.get('to', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')

        if not subject and not message:
            return JsonResponse({'status': 'success', 'message': 'Empty draft not saved'})

        # 1. ALWAYS SAVE LOCALLY FIRST (INSTANT)
        LocalDraft.objects.create(
            recipient=recipient,
            subject=subject,
            message=message
        )

        # 2. Try to sync to GoDaddy in the background
        try:
            from email.message import EmailMessage
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['To'] = recipient
            msg.set_content(message)

            possible_draft_folders = ['Drafts', 'INBOX.Drafts', 'Drafts Folder', 'Draft']
            
            with MailBox('imap.secureserver.net').login(GODADDY_EMAIL, GODADDY_PASSWORD) as mailbox:
                target_folder = 'INBOX'
                available_folders = [f.name for f in mailbox.folder.list()]
                for folder in possible_draft_folders:
                    if folder in available_folders:
                        target_folder = folder
                        break
                
                mailbox.folder.set(target_folder)
                mailbox.append(msg, flags=('\\Draft', '\\Seen'))
                return JsonResponse({'status': 'success', 'message': 'Draft saved locally & synced to server'})
        except Exception as e:
            # Even if GoDaddy fails, the local copy is safe!
            return JsonResponse({'status': 'success', 'message': 'Draft saved locally'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def toggle_pin_ajax(request):
    if not request.session.get('inbox_authenticated'):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    uid = request.POST.get('uid')
    folder = request.POST.get('folder', 'INBOX')
    subject = request.POST.get('subject', '')
    sender = request.POST.get('sender', '')
    snippet = request.POST.get('snippet', '')
    is_pinned = request.POST.get('is_pinned') == 'true'

    if not uid:
        return JsonResponse({'status': 'error', 'message': 'UID required'})

    try:
        if is_pinned:
            PinnedEmail.objects.update_or_create(
                uid=uid,
                folder=folder,
                defaults={'subject': subject, 'sender': sender, 'snippet': snippet},
            )
            return JsonResponse({'status': 'success', 'message': 'Email pinned'})

        PinnedEmail.objects.filter(uid=uid, folder=folder).delete()
        return JsonResponse({'status': 'success', 'message': 'Email unpinned'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def toggle_star_ajax(request):
    if not request.session.get('inbox_authenticated'):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    if request.method == "POST":
        uid = request.POST.get('uid')
        folder = request.POST.get('folder', 'INBOX')
        is_starred = request.POST.get('is_starred') == 'true'

        try:
            with MailBox('imap.secureserver.net').login(GODADDY_EMAIL, GODADDY_PASSWORD, folder) as mailbox:
                mailbox.flag(uid, '\\Flagged', is_starred)
                return JsonResponse({'status': 'success', 'message': 'Star toggled'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def save_settings_ajax(request):
    if not request.session.get('inbox_authenticated'):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    if request.method == "POST":
        try:
            settings_obj, _ = UserSettings.objects.get_or_create(email_account=GODADDY_EMAIL)
            settings_obj.emails_per_page = int(request.POST.get('emails_per_page', 50))
            settings_obj.inbox_type = request.POST.get('inbox_type', 'default')
            settings_obj.display_density = request.POST.get('display_density', 'default')
            settings_obj.theme = request.POST.get('theme', 'light')
            settings_obj.text_size = request.POST.get('text_size', 'Normal')
            settings_obj.save()
            return JsonResponse({'status': 'success', 'message': 'Settings saved'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def move_email_ajax(request):
    if not request.session.get('inbox_authenticated'):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    uid = request.GET.get('uid')
    source_folder = request.GET.get('folder', 'INBOX')
    target_type = request.GET.get('target') # 'Bin' or 'Spam'

    if not uid or not target_type:
        return JsonResponse({'status': 'error', 'message': 'Missing parameters'})

    try:
        with MailBox('imap.secureserver.net').login(GODADDY_EMAIL, GODADDY_PASSWORD, source_folder) as mailbox:
            # Detect actual target folder name
            available_folders = [f.name for f in mailbox.folder.list()]
            target_folder = None
            
            if target_type == 'Spam':
                for f in ['INBOX.Spam', 'Junk', 'Junk E-mail', 'Spam', 'SPAM']:
                    if f in available_folders:
                        target_folder = f
                        break
            elif target_type == 'Bin':
                for f in ['INBOX.Trash', 'Trash', 'Bin', 'Deleted Items', 'Deleted', 'DELETED']:
                    if f in available_folders:
                        target_folder = f
                        break
            elif target_type == 'Archive':
                for f in ['Archive', 'INBOX.Archive', 'All Mail', 'INBOX.All Mail']:
                    if f in available_folders:
                        target_folder = f
                        break
            elif target_type == 'Inbox':
                target_folder = 'INBOX'
            
            if not target_folder:
                return JsonResponse({'status': 'error', 'message': f'Target folder for {target_type} not found on server'})

            mailbox.move(uid, target_folder)
            return JsonResponse({'status': 'success', 'message': f'Email moved to {target_type}'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# from .models import PolicyDocument

def company_policy(request):
    documents = PolicyDocument.objects.all()
    return render(request, 'company_policy.html', {'documents': documents})