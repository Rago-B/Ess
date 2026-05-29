from django.core.management.base import BaseCommand
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings
from apps.visitor_management.models import Visitor
from datetime import datetime


class Command(BaseCommand):
    help = "Sync visitor data from Google Sheets"

    def handle(self, *args, **kwargs):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            settings.SERVICE_ACCOUNT_FILE, scope
        )
        client = gspread.authorize(creds)

        sheet = client.open("demo").sheet1
        rows = sheet.get_all_records()
        # print(rows[0].keys())


        for row in rows:
            timestamp_str = row.get('Timestamp')  
            check_in = None
            if timestamp_str:
                try:
                    check_in = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")
                except ValueError:
                    check_in = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M")

            Visitor.objects.get_or_create(
                      name=row.get('Name'),
                      email=row.get('Email'),
                      purpose=row.get('purpose'),            
                      check_in=check_in,                       
                      phone=row.get('Phone Number  '),
                      college_name=row.get('College Name'),
                      passed_out_year=row.get('Passed out year'),


                                     )


        self.stdout.write(self.style.SUCCESS("Visitor data synced successfully"))




# 1. Create a new Google Cloud project (or reuse the existing one)

# If you want to keep things separate, create a new project under the new Gmail.

# If you’re fine reusing, you can just add the new Gmail as an owner/editor to your current project.

# 2. Enable APIs again

# In the new project, enable both:

# Google Sheets API

# Google Drive API

# 3 .Create a new Service Account

# Go to IAM & Admin → Service Accounts.

# Create a new service account under the new Gmail project.

# Generate a JSON key file and download it.

# 4 . Update your Django settings

# Replace the old JSON file with the new one.

# Update settings.SERVICE_ACCOUNT_FILE to point to the new JSON file.

# 5 . Share the Google Sheet with the new service account email

# Open your sheet (e.g., “demo”).

# Click Share.

# Add the new service account email (something like xxxx@new-project.iam.gserviceaccount.com).

# Give it Editor access.