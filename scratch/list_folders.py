from imap_tools import MailBox

GODADDY_EMAIL = "sales@voxlom.com"
GODADDY_PASSWORD = "qwertya@123"

print("Checking GoDaddy IMAP folders...")
try:
    with MailBox('imap.secureserver.net').login(GODADDY_EMAIL, GODADDY_PASSWORD) as mailbox:
        for folder in mailbox.folder.list():
            print(f"Folder found: {folder.name}")
except Exception as e:
    print(f"Error: {e}")
