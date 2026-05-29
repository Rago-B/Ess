from django.urls import path
from . import views
from .test_imap import test_imap_view

urlpatterns = [
    path('login/', views.auth_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('test-imap/', test_imap_view, name='test_imap'),
    path('inbox-login-ajax/', views.inbox_login_ajax, name='inbox_login_ajax'),
    path('verify-otp-ajax/', views.verify_otp_ajax, name='verify_otp_ajax'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('fetch-email-content/', views.fetch_email_content_ajax, name='fetch_email_content'),
    path('send-email-ajax/', views.send_email_ajax, name='send_email_ajax'),
]