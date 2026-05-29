from django.db import models
from django.contrib.auth.models import User

class LocalDraft(models.Model):
    recipient = models.EmailField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Draft: {self.subject or '(No Subject)'}"

class SnoozedEmail(models.Model):
    uid = models.CharField(max_length=100)
    folder = models.CharField(max_length=100, default='INBOX')
    subject = models.CharField(max_length=255, blank=True, null=True)
    sender = models.CharField(max_length=255, blank=True, null=True)
    snooze_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Snoozed: {self.subject} until {self.snooze_until}"



class PinnedEmail(models.Model):
    uid = models.CharField(max_length=100)
    folder = models.CharField(max_length=100, default='INBOX')
    subject = models.CharField(max_length=255, blank=True, null=True)
    sender = models.CharField(max_length=255, blank=True, null=True)
    snippet = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('uid', 'folder')

    def __str__(self):
        return f"Pinned: {self.subject or self.uid}"


class UserSettings(models.Model):
    email_account = models.CharField(max_length=255, unique=True)
    emails_per_page = models.IntegerField(default=50)
    inbox_type = models.CharField(max_length=50, default='default')
    display_density = models.CharField(max_length=50, default='default')
    theme = models.CharField(max_length=50, default='light')
    text_size = models.CharField(max_length=20, default='Normal')
    
    def __str__(self):
        return f"Settings for {self.email_account}"




# class PolicyDocument(models.Model):
#     title       = models.CharField(max_length=200)
#     category    = models.CharField(max_length=100)
#     pdf_file    = models.FileField(upload_to='policy_docs/')
#     uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     uploaded_at = models.DateTimeField(auto_now_add=True)