from django.http import HttpResponse
from imap_tools import MailBox, A
import traceback

def test_imap_view(request):
  
    EMAIL = "sales@voxlom.com"
    PASSWORD = "qwertya@123"
    
    IMAP_HOST = "imap.secureserver.net"
    IMAP_PORT = 993

    html_content = "<h2>IMAP Test Route</h2>"

    try:
        # 1. Connect and login
        with MailBox(IMAP_HOST, port=IMAP_PORT).login(EMAIL, PASSWORD, 'INBOX') as mailbox:
            html_content += "<h3 style='color: green;'>IMAP Connection Successful!</h3>"
            
            # 2. Fetch latest 5 emails from Inbox
            html_content += "<h4>Latest 5 Emails:</h4>"
            html_content += "<ul>"
            
            # Fetching emails, reversing to get latest first, and taking up to 5
            emails = mailbox.fetch(limit=5, reverse=True)
            
            count = 0
            for msg in emails:
                html_content += f"<li><strong>Date:</strong> {msg.date} <br> <strong>Sender:</strong> {msg.from_} <br> <strong>Subject:</strong> {msg.subject}</li><br>"
                count += 1
                
            if count == 0:
                html_content += "<li>No emails found in the inbox.</li>"
                
            html_content += "</ul>"

    except Exception as e:
        # Connection or fetching failed
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        html_content += f"<h3 style='color: red;'>IMAP Connection Failed!</h3>"
        html_content += f"<p><strong>Error:</strong> {error_msg}</p>"
        html_content += f"<pre>{error_traceback}</pre>"

    return HttpResponse(html_content)
