import sys
from django.core.management.base import BaseCommand
from django.conf import settings
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class Command(BaseCommand):
    help = "Permanently remove a visitor row from Google Sheets using an isolated shell context"

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the visitor to delete')

    def handle(self, *args, **options):
        target_email = options['email'].strip().lower()

        # Uses the exact working credentials layout from your successful sync script
        scope = [
            "https://google.com",
            "https://googleapis.com"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            settings.SERVICE_ACCOUNT_FILE, scope
        )
        client = gspread.authorize(creds)
        sheet = client.open("demo").sheet1
        
        # Matches your screenshot layout: Email sits in Column C (3)
        email_column = sheet.col_values(3)
        cleaned_emails = [str(email).strip().lower() for email in email_column]

        if target_email in cleaned_emails:
            row_to_delete = cleaned_emails.index(target_email) + 1
            
            # Deletes the row instantly from the spreadsheet
            if hasattr(sheet, 'delete_rows'):
                sheet.delete_rows(row_to_delete)
            else:
                sheet.delete_row(row_to_delete)
                
            self.stdout.write(self.style.SUCCESS(f"✅ SUCCESS: Removed row {row_to_delete} from Google Sheets."))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ SKIPPED: '{target_email}' not found in Sheet."))
