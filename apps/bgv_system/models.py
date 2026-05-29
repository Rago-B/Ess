# Open apps/bgv_system/models.py
from django.db import models
from django.conf import settings
import uuid

class BGVWorkflowCheck(models.Model):
    STAGE_CHOICES = [
        ('Initiated', 'Initiated / Received'),
        ('Document Review', 'Document Under Review'),
        ('Approved', 'Passed / Cleared'),
        ('Rejected', 'Flagged / Failed'),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bgv_checks'
    )
    workflow_stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='Initiated')
    
    source_email = models.EmailField(verbose_name="Sender Email Address")
    email_message_id = models.CharField(max_length=255, unique=True, verbose_name="Unique Email UID")
    
    aadhar_file = models.FileField(upload_to='bgv_documents/aadhar/', blank=True, null=True)
    pan_file = models.FileField(upload_to='bgv_documents/pan/', blank=True, null=True)
    marksheet_file = models.FileField(upload_to='bgv_documents/marksheets/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"BGV File: {self.employee.email} [{self.workflow_stage}]"

# Open apps/bgv_system/models.py
from django.db import models
# Save in apps/bgv_system/models.py
from django.db import models

class UnknownCandidateBGVCheck(models.Model):
    # Unique reference tracking tokens generated automatically
    submission_id = models.CharField(
    max_length=50,
    unique=True,
    default=uuid.uuid4,
    editable=False
)
    
    
    # Core Identity Metric Columns
    aadhaar = models.CharField(max_length=20, blank=True, null=True, verbose_name="Aadhaar Number")
    pan = models.CharField(max_length=20, blank=True, null=True, verbose_name="PAN Card Number")
    course_type = models.CharField(max_length=255, blank=True, null=True, verbose_name="Course / Degree Type")
    
    # Physical File storage locations pointers path trackers
    marksheet_file = models.FileField(upload_to='candidate_documents/marksheets/', blank=True, null=True)
    experience_file = models.FileField(upload_to='candidate_documents/experience/', blank=True, null=True)
    
    # Dispatch tracking status parameters flags
    is_sent_to_bgv = models.BooleanField(default=False, verbose_name="Sent to BGV Agency Status")
    is_verified_by_officer = models.BooleanField(default=False)   # NEW FIELD
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Unknown Candidate BGV Check"
        verbose_name_plural = "Unknown Candidate BGV Checks"

    def __str__(self):
        return f"Unknown Ref: {self.submission_id} | Sent: {self.is_sent_to_bgv}"
